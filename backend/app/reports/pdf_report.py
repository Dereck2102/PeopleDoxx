from __future__ import annotations

import io
from datetime import datetime, timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.models.report import FullReport, ScraperResult
from app.reports.base_report import BaseReport

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
_BRAND_BLUE = colors.HexColor("#1A3C5E")
_BRAND_TEAL = colors.HexColor("#00897B")
_LIGHT_GREY = colors.HexColor("#F5F5F5")
_MID_GREY = colors.HexColor("#B0BEC5")
_SUCCESS_GREEN = colors.HexColor("#43A047")
_FAIL_RED = colors.HexColor("#E53935")
_TEXT_DARK = colors.HexColor("#212121")
_DISCLAIMER_GREY = colors.HexColor("#757575")

_PAGE_WIDTH, _PAGE_HEIGHT = A4
_MARGIN = 2 * cm


class PdfReport(BaseReport):
    """Generates a professional PDF report using ReportLab."""

    def generate(self, report: FullReport) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=_MARGIN,
            rightMargin=_MARGIN,
            topMargin=_MARGIN,
            bottomMargin=_MARGIN + 1.5 * cm,  # extra space for footer
        )

        styles = _build_styles()
        story = _build_story(report, styles)

        doc.build(
            story,
            onFirstPage=_draw_header_footer,
            onLaterPages=_draw_header_footer,
        )
        buffer.seek(0)
        return buffer.read()


# ---------------------------------------------------------------------------
# Style helpers
# ---------------------------------------------------------------------------

def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title",
            parent=base["Title"],
            fontSize=22,
            textColor=_BRAND_BLUE,
            alignment=TA_LEFT,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            parent=base["Normal"],
            fontSize=10,
            textColor=_MID_GREY,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "section_header": ParagraphStyle(
            "section_header",
            parent=base["Heading2"],
            fontSize=13,
            textColor=colors.white,
            backColor=_BRAND_BLUE,
            spaceBefore=12,
            spaceAfter=4,
            leftIndent=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontSize=9,
            textColor=_TEXT_DARK,
            leading=14,
        ),
        "disclaimer": ParagraphStyle(
            "disclaimer",
            parent=base["Normal"],
            fontSize=7,
            textColor=_DISCLAIMER_GREY,
            alignment=TA_CENTER,
            spaceBefore=16,
        ),
        "label": ParagraphStyle(
            "label",
            parent=base["Normal"],
            fontSize=9,
            textColor=_BRAND_BLUE,
            fontName="Helvetica-Bold",
        ),
        "value": ParagraphStyle(
            "value",
            parent=base["Normal"],
            fontSize=9,
            textColor=_TEXT_DARK,
        ),
        "error": ParagraphStyle(
            "error",
            parent=base["Normal"],
            fontSize=9,
            textColor=_FAIL_RED,
            fontName="Helvetica-Oblique",
        ),
    }


# ---------------------------------------------------------------------------
# Story builder
# ---------------------------------------------------------------------------

def _build_story(report: FullReport, styles: dict) -> list:
    meta = report.metadata
    story: list = []

    # ---- Title block -------------------------------------------------------
    story.append(Paragraph("PeopleDoxx", styles["title"]))
    story.append(
        Paragraph(
            "Reporte OSINT de Fuentes Públicas Gubernamentales del Ecuador",
            styles["subtitle"],
        )
    )
    story.append(HRFlowable(width="100%", thickness=2, color=_BRAND_TEAL))
    story.append(Spacer(1, 0.4 * cm))

    # ---- Summary table -----------------------------------------------------
    generated_at_str = meta.generated_at.strftime("%d/%m/%Y %H:%M:%S UTC")
    summary_data = [
        ["Campo", "Valor"],
        ["Cédula Consultada", meta.cedula],
        ["Fecha de Generación", generated_at_str],
        ["Total de Fuentes", str(meta.total_sources)],
        ["Fuentes Exitosas", str(meta.successful_sources)],
        ["Fuentes Fallidas", str(meta.failed_sources)],
    ]
    summary_table = Table(
        summary_data,
        colWidths=[(_PAGE_WIDTH - 2 * _MARGIN) * 0.4, (_PAGE_WIDTH - 2 * _MARGIN) * 0.6],
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _BRAND_BLUE),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BACKGROUND", (0, 1), (-1, -1), _LIGHT_GREY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT_GREY]),
                ("GRID", (0, 0), (-1, -1), 0.5, _MID_GREY),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 0.6 * cm))

    # ---- Per-scraper sections ----------------------------------------------
    for result in report.results:
        story.extend(_build_scraper_section(result, styles))

    # ---- Disclaimer --------------------------------------------------------
    story.append(
        Paragraph(
            "AVISO: Información obtenida de fuentes públicas gubernamentales. "
            "Uso exclusivo para fines legales y autorizados. "
            "PeopleDoxx no almacena datos personales de forma permanente.",
            styles["disclaimer"],
        )
    )
    return story


def _build_scraper_section(result: ScraperResult, styles: dict) -> list:
    elements: list = []

    # Section header with status indicator
    status_color = _SUCCESS_GREEN if result.success else _FAIL_RED
    status_text = "[OK]" if result.success else "[FALLO]"
    header_text = (
        f'<font color="white">{status_text} {result.source_name} '
        f'<font size="8">({result.source})</font></font>'
    )
    elements.append(Paragraph(header_text, styles["section_header"]))

    if not result.success:
        error_msg = result.error or "Error desconocido"
        elements.append(
            Paragraph(f"Error: {error_msg}", styles["error"])
        )
        elements.append(Spacer(1, 0.3 * cm))
        return elements

    # Build key-value table from data dict
    flat = _flatten_dict(result.data)
    if not flat:
        elements.append(Paragraph("No se obtuvieron datos.", styles["body"]))
        elements.append(Spacer(1, 0.3 * cm))
        return elements

    table_data = [["Campo", "Valor"]]
    for key, value in flat.items():
        display_key = key.replace("_", " ").title()
        table_data.append([display_key, str(value) if value is not None else "—"])

    col_width = _PAGE_WIDTH - 2 * _MARGIN
    kv_table = Table(
        table_data,
        colWidths=[col_width * 0.38, col_width * 0.62],
        repeatRows=1,
    )
    kv_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), _BRAND_TEAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, _LIGHT_GREY]),
                ("GRID", (0, 0), (-1, -1), 0.4, _MID_GREY),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("WORDWRAP", (1, 0), (1, -1), True),
            ]
        )
    )
    elements.append(kv_table)
    elements.append(Spacer(1, 0.4 * cm))
    return elements


# ---------------------------------------------------------------------------
# Page decorators (header / footer on every page)
# ---------------------------------------------------------------------------

def _draw_header_footer(canvas, doc) -> None:  # type: ignore[no-untyped-def]
    canvas.saveState()
    page_width = A4[0]

    # Thin top rule
    canvas.setStrokeColor(_BRAND_TEAL)
    canvas.setLineWidth(1.5)
    canvas.line(_MARGIN, _PAGE_HEIGHT - _MARGIN * 0.6, page_width - _MARGIN, _PAGE_HEIGHT - _MARGIN * 0.6)

    # Footer rule
    canvas.setStrokeColor(_MID_GREY)
    canvas.setLineWidth(0.5)
    footer_y = _MARGIN - 0.2 * cm
    canvas.line(_MARGIN, footer_y, page_width - _MARGIN, footer_y)

    # Footer text
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(_DISCLAIMER_GREY)
    canvas.drawString(
        _MARGIN,
        footer_y - 0.4 * cm,
        f"PeopleDoxx — Generado el {datetime.now(tz=timezone.utc).strftime('%d/%m/%Y %H:%M UTC')}",
    )
    canvas.drawRightString(
        page_width - _MARGIN,
        footer_y - 0.4 * cm,
        f"Página {doc.page}",
    )
    canvas.restoreState()


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _flatten_dict(d: dict, prefix: str = "", sep: str = ".") -> dict[str, object]:
    """Recursively flatten a nested dict into dot-separated keys."""
    items: dict[str, object] = {}
    for key, value in d.items():
        new_key = f"{prefix}{sep}{key}" if prefix else key
        if isinstance(value, dict):
            items.update(_flatten_dict(value, new_key, sep))
        elif isinstance(value, list):
            if not value:
                items[new_key] = "—"
            else:
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        items.update(_flatten_dict(item, f"{new_key}[{i}]", sep))
                    else:
                        items[f"{new_key}[{i}]"] = item
        else:
            items[new_key] = value
    return items
