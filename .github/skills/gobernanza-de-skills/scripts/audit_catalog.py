#!/usr/bin/env python3
"""Audita un catálogo de skills (carpetas que contienen SKILL.md).

Uso:
    python audit_catalog.py --root RUTA [--json salida.json]

Comprueba: frontmatter, name/description, nombre = carpeta, longitud de la
descripción y del cuerpo, nombres duplicados y enlaces o rutas rotas.
Solo usa la biblioteca estándar; si PyYAML está instalado, valida el YAML.
Código de salida: 1 si hay errores, 0 si no.
"""
import argparse
import json
import re
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
PATH_RE = re.compile(r"`((?:references|scripts|assets|examples|resources)/[^`\s]+)`")
TRIGGER_HINTS = ("cuando", "úsala", "usala", "use when", "ante ", "al ", "para ")
MAX_NAME = 64
MAX_DESC_HARD = 1024      # límite del estándar abierto de skills
MAX_DESC_SOFT = 300       # la descripción cuesta contexto en cada turno
MAX_BODY_LINES = 500


def split_frontmatter(text):
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1:])
    return None, text


def parse_simple(fm):
    """Parser mínimo de claves de primer nivel (escalares, comillas, > y |)."""
    data, key, buf, folded = {}, None, [], False
    for raw in fm.splitlines():
        if re.match(r"^[A-Za-z_][\w-]*:", raw):
            if key is not None:
                data[key] = " ".join(buf).strip() if folded else (buf[0] if buf else "")
            key, val = raw.split(":", 1)
            val = val.strip()
            folded = val in (">", "|", ">-", "|-")
            buf = [] if folded else [val.strip("\"'")]
        elif key is not None and raw.startswith((" ", "\t")) and folded:
            buf.append(raw.strip())
    if key is not None:
        data[key] = " ".join(buf).strip() if folded else (buf[0] if buf else "")
    return data


def parse_frontmatter(fm):
    try:
        import yaml  # type: ignore
        parsed = yaml.safe_load(fm)
        if not isinstance(parsed, dict):
            raise ValueError("el frontmatter no es un mapa")
        return {k: ("" if v is None else v) for k, v in parsed.items()}, None
    except ImportError:
        return parse_simple(fm), None
    except Exception as exc:  # YAML inválido
        return {}, f"frontmatter YAML inválido: {exc}"


def audit_skill(skill_md):
    issues = []

    def add(level, msg):
        issues.append({"level": level, "message": msg})

    text = skill_md.read_text(encoding="utf-8")
    fm_text, body = split_frontmatter(text)
    folder = skill_md.parent.name
    meta = {}
    if fm_text is None:
        add("error", "falta el frontmatter YAML (--- ... ---)")
    else:
        meta, err = parse_frontmatter(fm_text)
        if err:
            add("error", err)

    name = str(meta.get("name", "")).strip()
    desc = str(meta.get("description", "")).strip()

    if not desc and fm_text is not None and not issues:
        add("error", "falta `description` (obligatoria)")
    if name:
        if len(name) > MAX_NAME or not NAME_RE.match(name):
            add("error", f"`name` inválido: '{name}' (minúsculas, números y guiones; máx. {MAX_NAME})")
        if name != folder:
            add("warn", f"`name` ('{name}') no coincide con la carpeta ('{folder}')")
    if desc:
        if len(desc) > MAX_DESC_HARD:
            add("error", f"descripción de {len(desc)} caracteres (máx. {MAX_DESC_HARD})")
        elif len(desc) > MAX_DESC_SOFT:
            add("warn", f"descripción larga ({len(desc)} caracteres): cuesta contexto en cada turno")
        if not any(h in desc.lower() for h in TRIGGER_HINTS):
            add("warn", "la descripción no indica cuándo usar la skill")

    body_lines = len(body.splitlines())
    if body_lines > MAX_BODY_LINES:
        add("warn", f"cuerpo de {body_lines} líneas (recomendado < {MAX_BODY_LINES}); mueve detalle a references/")

    base = skill_md.parent
    seen = set()
    refs = [m for m in LINK_RE.findall(body)] + [m for m in PATH_RE.findall(body)]
    for ref in refs:
        if ref in seen:
            continue
        seen.add(ref)
        if ref.startswith(("http://", "https://", "mailto:", "#")) or any(c in ref for c in "*<>{}"):
            continue
        target = (base / ref.split("#", 1)[0]).resolve()
        if not target.exists():
            add("error", f"referencia rota: {ref}")
    return {"path": str(skill_md), "name": name or folder, "issues": issues}


def main():
    ap = argparse.ArgumentParser(description="Audita un catálogo de skills.")
    ap.add_argument("--root", default=".", help="carpeta que contiene las skills (se busca SKILL.md recursivamente)")
    ap.add_argument("--json", dest="json_out", help="guarda los resultados en este archivo JSON")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print(f"No existe: {root}", file=sys.stderr)
        return 2
    files = sorted(root.rglob("SKILL.md"))
    if not files:
        print("No se encontró ningún SKILL.md.", file=sys.stderr)
        return 2

    results = [audit_skill(f) for f in files]
    names = {}
    for r in results:
        names.setdefault(r["name"], []).append(r["path"])
    for n, paths in names.items():
        if len(paths) > 1:
            for r in results:
                if r["name"] == n:
                    r["issues"].append({"level": "error", "message": f"nombre duplicado '{n}' en {len(paths)} skills"})

    errors = sum(1 for r in results for i in r["issues"] if i["level"] == "error")
    warns = sum(1 for r in results for i in r["issues"] if i["level"] == "warn")
    for r in results:
        status = "OK " if not r["issues"] else ("ERR" if any(i["level"] == "error" for i in r["issues"]) else "WRN")
        print(f"[{status}] {r['name']}")
        for i in r["issues"]:
            print(f"      {i['level']}: {i['message']}")
    print(f"\n{len(results)} skills · {errors} errores · {warns} avisos")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps({"skills": results, "errors": errors, "warnings": warns}, ensure_ascii=False, indent=2),
            encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
