#!/usr/bin/env python3
"""
PeopleDoxx CLI — Herramienta de línea de comandos para consulta de información pública.

Uso:
    peopledoxx search --cedula 1713175071
    peopledoxx search --cedula 1713175071 --format pdf --output ./reporte.pdf
    peopledoxx sources
"""

import asyncio
import json
import sys
from pathlib import Path

import click
import httpx


API_BASE_URL = "http://localhost:8000"


def validate_cedula_format(ctx, param, value):
    """Validación básica de formato de cédula."""
    if not value or not value.isdigit() or len(value) != 10:
        raise click.BadParameter("La cédula debe tener exactamente 10 dígitos numéricos.")
    return value


@click.group()
@click.version_option(version="1.0.0", prog_name="PeopleDoxx")
def cli():
    """
    \b
    ██████╗ ███████╗ ██████╗ ██████╗ ██╗     ███████╗
    ██╔══██╗██╔════╝██╔═══██╗██╔══██╗██║     ██╔════╝
    ██████╔╝█████╗  ██║   ██║██████╔╝██║     █████╗
    ██╔═══╝ ██╔══╝  ██║   ██║██╔═══╝ ██║     ██╔══╝
    ██║     ███████╗╚██████╔╝██║     ███████╗███████╗
    ╚═╝     ╚══════╝ ╚═════╝ ╚═╝     ╚══════╝╚══════╝
     ██████╗  ██████╗ ██╗  ██╗██╗  ██╗
    ██╔══██╗██╔═══██╗╚██╗██╔╝╚██╗██╔╝
    ██║  ██║██║   ██║ ╚███╔╝  ╚███╔╝
    ██║  ██║██║   ██║ ██╔██╗  ██╔██╗
    ██████╔╝╚██████╔╝██╔╝ ██╗██╔╝ ██╗
    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝

    Consulta información pública desde fuentes gubernamentales ecuatorianas.
    Solo para uso legal y autorizado.
    """


@cli.command()
@click.option(
    "--cedula",
    "-c",
    required=True,
    callback=validate_cedula_format,
    help="Número de cédula ecuatoriana (10 dígitos).",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["json", "pdf", "table"], case_sensitive=False),
    default="table",
    show_default=True,
    help="Formato de salida del reporte.",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Ruta de archivo de salida (para json o pdf).",
)
@click.option(
    "--api-key",
    envvar="PEOPLEDOXX_API_KEY",
    default="dev-key-change-in-production",
    help="API key para autenticación (o variable PEOPLEDOXX_API_KEY).",
)
@click.option(
    "--api-url",
    envvar="PEOPLEDOXX_API_URL",
    default=API_BASE_URL,
    show_default=True,
    help="URL base de la API de PeopleDoxx.",
)
def search(cedula: str, output_format: str, output: str | None, api_key: str, api_url: str):
    """Busca información pública de una persona por cédula ecuatoriana."""
    asyncio.run(_search(cedula, output_format, output, api_key, api_url))


async def _search(cedula: str, output_format: str, output: str | None, api_key: str, api_url: str):
    headers = {"X-API-Key": api_key, "Content-Type": "application/json"}

    click.echo(f"\n[INFO] Buscando información para cédula: {click.style(cedula, bold=True, fg='cyan')}")
    click.echo("[INFO] Consultando fuentes gubernamentales...\n")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if output_format == "pdf":
                response = await client.get(
                    f"{api_url}/api/v1/reports/{cedula}/pdf",
                    headers=headers,
                )
                response.raise_for_status()

                out_path = output or f"reporte_{cedula}.pdf"
                Path(out_path).write_bytes(response.content)
                click.echo(f"[OK] Reporte PDF guardado en: {click.style(out_path, fg='green', bold=True)}")

            elif output_format == "json":
                response = await client.get(
                    f"{api_url}/api/v1/reports/{cedula}/json",
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                out_path = output or f"reporte_{cedula}.json"
                Path(out_path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                click.echo(f"[OK] Reporte JSON guardado en: {click.style(out_path, fg='green', bold=True)}")

            else:  # table
                response = await client.post(
                    f"{api_url}/api/v1/search",
                    headers=headers,
                    json={"cedula": cedula},
                )
                response.raise_for_status()
                data = response.json()
                _print_table(data)

    except httpx.ConnectError:
        click.echo(
            click.style(
                f"\n[ERROR] No se pudo conectar a la API en {api_url}\n"
                "   Asegúrate de que el backend está corriendo: docker compose up backend",
                fg="red",
            )
        )
        sys.exit(1)
    except httpx.HTTPStatusError as e:
        click.echo(click.style(f"\n[ERROR] HTTP {e.response.status_code}: {e.response.text}", fg="red"))
        sys.exit(1)


def _print_table(data: dict):
    """Imprime los resultados en formato tabla en consola."""
    cedula = data.get("cedula", "")
    total = data.get("total_sources", 0)
    successful = data.get("successful_sources", 0)
    results = data.get("results", [])

    click.echo("=" * 70)
    click.echo(f"  REPORTE DE INFORMACIÓN PÚBLICA — CÉDULA {cedula}")
    click.echo("=" * 70)
    click.echo(
        f"  Fuentes consultadas: {total}  |  "
        f"Exitosas: {click.style(str(successful), fg='green')}  |  "
        f"Fallidas: {click.style(str(total - successful), fg='red')}"
    )
    click.echo("=" * 70)

    for result in results:
        source_name = result.get("source_name", result.get("source", ""))
        success = result.get("success", False)
        status_icon = click.style("[OK]", fg="green") if success else click.style("[FALLO]", fg="red")
        duration = result.get("duration_ms", 0)

        click.echo(f"\n{status_icon} {click.style(source_name, bold=True)} ({duration:.0f}ms)")
        click.echo("-" * 60)

        if success:
            payload = result.get("data", {})
            if not payload:
                click.echo("  (Sin datos retornados)")
            else:
                for key, value in payload.items():
                    label = key.replace("_", " ").title()
                    if isinstance(value, (dict, list)):
                        value_str = json.dumps(value, ensure_ascii=False, indent=2)
                    else:
                        value_str = str(value)
                    click.echo(f"  {click.style(label + ':', bold=True):30} {value_str}")
        else:
            error = result.get("error", "Error desconocido")
            click.echo(f"  {click.style('Error:', fg='red')} {error}")

    click.echo("\n" + "=" * 70)
    click.echo(
        click.style(
            "[AVISO] Información obtenida de fuentes públicas gubernamentales.\n"
            "   Uso exclusivo para fines legales y autorizados.",
            fg="yellow",
        )
    )
    click.echo("=" * 70 + "\n")


@cli.command()
@click.option("--api-url", envvar="PEOPLEDOXX_API_URL", default=API_BASE_URL)
@click.option("--api-key", envvar="PEOPLEDOXX_API_KEY", default="dev-key-change-in-production")
def sources(api_url: str, api_key: str):
    """Lista las fuentes gubernamentales disponibles."""
    headers = {"X-API-Key": api_key}

    async def _list():
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{api_url}/api/v1/search/sources", headers=headers)
                response.raise_for_status()
                srcs = response.json()

                click.echo("\nFuentes gubernamentales disponibles:\n")
                for src in srcs:
                    enabled = "[ACTIVO]" if src.get("enabled", True) else "[INACTIVO]"
                    click.echo(f"  {enabled} {click.style(src['source_id'], bold=True, fg='cyan'):10} — {src['source_name']}")
                    click.echo(f"      URL: {src.get('base_url', 'N/A')}")
                click.echo()
        except Exception as e:
            click.echo(click.style(f"[ERROR] {e}", fg="red"))

    asyncio.run(_list())


@cli.command()
@click.option("--api-url", envvar="PEOPLEDOXX_API_URL", default=API_BASE_URL)
def health(api_url: str):
    """Verifica el estado del backend de PeopleDoxx."""

    async def _check():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{api_url}/health")
                if response.status_code == 200:
                    data = response.json()
                    click.echo(click.style(f"[OK] Backend saludable — {data}", fg="green"))
                else:
                    click.echo(click.style(f"[ADVERTENCIA] Backend respondió con status {response.status_code}", fg="yellow"))
        except httpx.ConnectError:
            click.echo(click.style(f"[ERROR] No se puede conectar a {api_url}", fg="red"))
            sys.exit(1)

    asyncio.run(_check())


if __name__ == "__main__":
    cli()

