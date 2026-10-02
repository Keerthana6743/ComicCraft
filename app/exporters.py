"""
ComicCraft - PDF Exporter
Team ID: 6ab22cb7

Generates a downloadable multi-page comic book PDF using FPDF / FPDF2.
Features cover page, framed panel illustrations, styled caption boxes,
and character dialogue speech bubbles.
"""

import os
import time
import logging
from typing import List, Dict, Any, Optional
from fpdf import FPDF

logger = logging.getLogger(__name__)


def _sanitize_pdf_text(text: str) -> str:
    """
    Sanitize text to prevent FPDF Latin-1 encoding errors while preserving readability.
    Replaces smart quotes, em-dashes, and special symbols with standard ASCII equivalents.
    """
    if not text:
        return ""
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2014": " - ",
        "\u2013": " - ",
        "\u2026": "...",
        "\u00a0": " ",
        "•": "*",
        "’": "'",
        "“": '"',
        "”": '"'
    }
    for orig, rep in replacements.items():
        text = text.replace(orig, rep)
    # Filter any remaining non-latin1 characters
    return text.encode("latin-1", "replace").decode("latin-1")


class ComicBookPDF(FPDF):
    """Custom FPDF class tailored for high-impact Comic Book formatting."""

    def __init__(self, comic_title: str = "ComicCraft Comic", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.comic_title = _sanitize_pdf_text(comic_title)
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        """Top comic strip banner on every page."""
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(120, 120, 140)
            self.cell(0, 8, f"COMICCRAFT  |  {self.comic_title.upper()[:45]}", border="B", ln=1, align="L")
            self.ln(4)

    def footer(self):
        """Bottom page footer."""
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 160)
        self.cell(0, 8, f"Page {self.page_no()}  *  ComicCraft AI - Team 6ab22cb7", align="C")


def save_pdf(
    comic_title: str,
    panels: List[Dict[str, Any]],
    output_dir: str = "static/exports",
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Build and save a multi-page comic book PDF.

    Args:
        comic_title: Story prompt or chosen title of the comic.
        panels: List of unified panel dictionaries from layout_builder.
        output_dir: Destination directory (default: 'static/exports').
        metadata: Optional metadata dictionary (character, setting, tone, art_style).

    Returns:
        Web-accessible relative URL path, e.g. '/static/exports/comic_1711929381.pdf'
    """
    os.makedirs(output_dir, exist_ok=True)
    meta = metadata or {}

    timestamp = int(time.time())
    filename = f"comic_{timestamp}.pdf"
    filepath = os.path.join(output_dir, filename)

    pdf = ComicBookPDF(comic_title=comic_title, orientation="P", unit="mm", format="A4")
    # A4 Dimensions: 210mm x 297mm

    # =========================================================================
    # 1. COVER PAGE
    # =========================================================================
    pdf.add_page()

    # Dark background accent frame for cover
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(10, 10, 190, 277, style="F")

    # Inner decorative border
    pdf.set_draw_color(250, 204, 21)  # Golden comic yellow
    pdf.set_line_width(1.5)
    pdf.rect(14, 14, 182, 269)
    pdf.set_draw_color(239, 68, 68)  # Red accent line
    pdf.set_line_width(0.6)
    pdf.rect(16, 16, 178, 265)

    # ComicCraft Top Badge
    pdf.set_y(26)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(239, 68, 68)
    pdf.cell(0, 8, "C O M I C C R A F T   P R E S E N T S", ln=1, align="C")

    # Main Comic Title
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(255, 255, 255)
    clean_title = _sanitize_pdf_text(comic_title)
    if len(clean_title) > 80:
        clean_title = clean_title[:77] + "..."
    pdf.multi_cell(0, 11, clean_title.upper(), align="C")

    # Decorative dividing bar
    pdf.ln(4)
    pdf.set_fill_color(250, 204, 21)
    pdf.rect(65, pdf.get_y(), 80, 2, style="F")
    pdf.ln(8)

    # Feature Preview: Panel 1 Image on Cover if available
    first_panel_img = None
    if panels and len(panels) > 0:
        first_img_rel = panels[0].get("image_path", "").lstrip("/")
        if os.path.exists(first_img_rel):
            first_panel_img = first_img_rel

    if first_panel_img:
        try:
            # Center image on cover
            img_w, img_h = 110, 110
            img_x = (210 - img_w) / 2
            curr_y = pdf.get_y()
            # Draw frame behind image
            pdf.set_fill_color(0, 0, 0)
            pdf.rect(img_x - 3, curr_y - 3, img_w + 6, img_h + 6, style="F")
            pdf.image(first_panel_img, x=img_x, y=curr_y, w=img_w, h=img_h)
            pdf.set_y(curr_y + img_h + 10)
        except Exception as err:
            logger.warning(f"Could not place cover image: {err}")
            pdf.ln(115)
    else:
        pdf.ln(115)

    # Story Metadata Badges Box
    meta_box_y = pdf.get_y()
    pdf.set_fill_color(30, 41, 59)
    pdf.set_draw_color(56, 189, 248)
    pdf.set_line_width(0.5)
    pdf.rect(25, meta_box_y, 160, 42, style="FD")

    pdf.set_y(meta_box_y + 4)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(56, 189, 248)
    pdf.cell(0, 6, "STORY SPECIFICATIONS", ln=1, align="C")

    character = _sanitize_pdf_text(meta.get("character", "Hero"))
    setting = _sanitize_pdf_text(meta.get("setting", "Mystic Realm"))
    tone = _sanitize_pdf_text(meta.get("tone", "Adventure"))
    art_style = _sanitize_pdf_text(meta.get("art_style", "Comic Book"))

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(241, 245, 249)
    pdf.set_x(30)
    pdf.cell(75, 6, f"Character: {character}", align="L")
    pdf.cell(75, 6, f"Tone: {tone}", ln=1, align="L")
    pdf.set_x(30)
    pdf.cell(75, 6, f"Setting: {setting}", align="L")
    pdf.cell(75, 6, f"Art Style: {art_style}", ln=1, align="L")

    # Team & Credits Badge
    pdf.set_y(meta_box_y + 48)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(250, 204, 21)
    pdf.cell(0, 6, "AI Powered Storytelling * Team ID: 6ab22cb7 * ComicCraft", ln=1, align="C")

    # =========================================================================
    # 2. STORY PANELS (1 per page for maximum visual clarity & comic magazine feel)
    # =========================================================================
    for panel in panels:
        pdf.add_page()

        panel_num = panel.get("panel_number", 1)
        title = _sanitize_pdf_text(panel.get("title", f"Panel {panel_num}"))
        narration = _sanitize_pdf_text(panel.get("narration", ""))
        dialogue = _sanitize_pdf_text(panel.get("dialogue", ""))
        scene_desc = _sanitize_pdf_text(panel.get("scene_description", ""))
        img_rel = panel.get("image_path", "").lstrip("/")

        # Panel Header / Title Banner
        pdf.set_fill_color(239, 68, 68)  # Comic Red
        pdf.set_draw_color(0, 0, 0)
        pdf.set_line_width(0.8)
        pdf.rect(15, 22, 180, 11, style="FD")

        pdf.set_y(23)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 9, f"PANEL {panel_num}: {title.upper()}", ln=1, align="C")

        pdf.ln(5)

        # Panel Image with comic frame
        img_w, img_h = 135, 135
        img_x = (210 - img_w) / 2
        img_y = pdf.get_y()

        # Check if image file exists
        if os.path.exists(img_rel):
            try:
                # Black outer shadow/border
                pdf.set_fill_color(0, 0, 0)
                pdf.rect(img_x - 2, img_y - 2, img_w + 4, img_h + 4, style="F")
                pdf.image(img_rel, x=img_x, y=img_y, w=img_w, h=img_h)
            except Exception as e:
                logger.warning(f"Error rendering image for panel {panel_num}: {e}")
                pdf.rect(img_x, img_y, img_w, img_h, style="D")
        else:
            pdf.set_fill_color(240, 240, 240)
            pdf.rect(img_x, img_y, img_w, img_h, style="FD")
            pdf.set_y(img_y + 60)
            pdf.set_font("Helvetica", "I", 11)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(0, 10, "[ Comic Panel Illustration ]", align="C")

        # Position below image
        content_y = img_y + img_h + 8
        pdf.set_y(content_y)

        # 1. Narration Box (Classic Comic Yellow Caption Box)
        if narration:
            pdf.set_fill_color(254, 240, 138)  # Bright comic caption yellow
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.7)
            # Estimate height for narration box
            box_height = 24
            pdf.rect(15, content_y, 180, box_height, style="FD")

            pdf.set_xy(18, content_y + 2)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(180, 83, 9)  # Amber title
            pdf.cell(0, 4, "NARRATION:", ln=1, align="L")

            pdf.set_x(18)
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(15, 23, 42)
            pdf.multi_cell(174, 5, narration, align="L")

            content_y += box_height + 5

        # 2. Dialogue Box (Comic Speech Balloon style)
        if dialogue:
            pdf.set_fill_color(255, 255, 255)
            pdf.set_draw_color(37, 99, 235)  # Comic Blue border
            pdf.set_line_width(0.8)
            dialogue_box_height = 24
            pdf.rect(15, content_y, 180, dialogue_box_height, style="FD")

            pdf.set_xy(18, content_y + 2)
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(37, 99, 235)
            pdf.cell(0, 4, "DIALOGUE:", ln=1, align="L")

            pdf.set_x(18)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(15, 23, 42)
            pdf.multi_cell(174, 5, dialogue, align="L")

    # Output to disk
    pdf.output(filepath)
    logger.info(f"Comic PDF exported successfully: {filepath}")

    return f"/{output_dir.replace(os.sep, '/')}/{filename}"
