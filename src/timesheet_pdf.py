
import io
import os
from pathlib import Path
import configparser as cp

import pandas as pd

from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.pdfbase.pdfmetrics import stringWidth
from PyPDF2 import PdfReader, PdfWriter


def build_cust_pdf(cust: str, df: pd.DataFrame):
    # --- Paths ---
    SCRIPT_DIR = Path(__file__).resolve().parent
    CONFIG_PATH = SCRIPT_DIR / "config.properties"
    PDF_FN = f"scratch/{cust}_timesheet.pdf"
    PDF_PATH = SCRIPT_DIR / PDF_FN

    # Ensure output folder exists
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)

    # --- Load configuration (use str path) ---
    config = cp.ConfigParser()
    config.read(os.fspath(CONFIG_PATH))

    # ----------------------------
    # Build table Flowables (no build here)
    # ----------------------------
    def build_table_flowables(
        df: pd.DataFrame,
        page_size=A4,
        landscape_mode: bool = True,
        margins_mm: float = 8.0,
        rows_per_page: int = 35,
        min_col_width_pt: float = 36.0,
        max_col_width_ratio: float = 0.45,
        notes_col_name: str = "Notes",
        notes_weight: float = 3.0,
        notes_max_ratio: float = 0.50,
    ):
        page_size = landscape(page_size) if landscape_mode else page_size

        left_margin = margins_mm * mm
        right_margin = margins_mm * mm

        styles = getSampleStyleSheet()
        normal = styles["Normal"]
        normal.fontName = "Helvetica"
        normal.fontSize = 8.5
        normal.leading = 10.5

        header_font_name = "Helvetica-Bold"
        header_font_size = 8.5

        cell_lr_padding = 3  # per side
        cell_tb_padding = 2  # per side
        total_cell_hpad = cell_lr_padding * 2

        def df_to_rows(dfi: pd.DataFrame):
            header = list(map(str, dfi.columns))
            data_rows = []
            for _, row in dfi.iterrows():
                cells = []
                for col in dfi.columns:
                    val = row[col]
                    txt = "" if pd.isna(val) else str(val)
                    cells.append(Paragraph(txt, normal))
                data_rows.append(cells)
            return [header] + data_rows

        def compute_column_widths(df_all: pd.DataFrame, available_width: float):
            cols = list(df_all.columns)

            header_widths = [
                stringWidth(str(col), header_font_name, header_font_size) + total_cell_hpad
                for col in cols
            ]

            content_widths = []
            for col in cols:
                max_w = 0.0
                for val in df_all[col].astype(str).fillna(""):
                    w = stringWidth(val, normal.fontName, normal.fontSize)
                    if w > max_w:
                        max_w = w
                content_widths.append(max_w + total_cell_hpad)

            base_desired = [max(h, c) for h, c in zip(header_widths, content_widths)]

            # Weights: give Notes more room
            weights = [(notes_weight if col == notes_col_name else 1.0) for col in cols]
            total_weight = sum(weights)
            weight_dist = [available_width * (w / total_weight) for w in weights]

            generic_max_pt = available_width * max_col_width_ratio
            widths = []
            for i, col in enumerate(cols):
                w = max(base_desired[i], weight_dist[i])
                w = max(w, min_col_width_pt)
                if col == notes_col_name:
                    w = min(w, available_width * notes_max_ratio)
                else:
                    w = min(w, generic_max_pt)
                widths.append(w)

            total_w = sum(widths)
            if total_w > available_width and total_w > 0:
                scale = available_width / total_w
                widths = [w * scale for w in widths]

            return widths

        elements = []
        total_rows = len(df)
        start = 0

        page_width = page_size[0]
        usable_width = page_width - left_margin - right_margin
        column_widths = compute_column_widths(df, usable_width)

        while start < total_rows:
            end = min(start + rows_per_page, total_rows)
            chunk = df.iloc[start:end]
            table_data = df_to_rows(chunk)

            tbl = Table(table_data, colWidths=column_widths, repeatRows=1)
            tbl_style = TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("FONTNAME", (0, 0), (-1, 0), header_font_name),
                ("FONTSIZE", (0, 0), (-1, 0), header_font_size),
                ("FONTNAME", (0, 1), (-1, -1), normal.fontName),
                ("FONTSIZE", (0, 1), (-1, -1), normal.fontSize),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#aaaaaa")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#fbfbfb")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), cell_lr_padding),
                ("RIGHTPADDING", (0, 0), (-1, -1), cell_lr_padding),
                ("TOPPADDING", (0, 0), (-1, -1), cell_tb_padding),
                ("BOTTOMPADDING", (0, 0), (-1, -1), cell_tb_padding),
            ])
            tbl.setStyle(tbl_style)

            elements.append(tbl)
            start = end
            if start < total_rows:
                elements.append(PageBreak())

        return elements

    # ----------------------------
    # Signature block (Flowables)
    # ----------------------------
    def build_signature_block(
        person_name: str,
        blank_lines: int = 2,
        print_blank_lines_above: bool = True,
        label_font: str = "Helvetica",
        label_font_size: float = 10.0,
        line_char_count_signature: int = 30,
        line_char_count_date: int = 10,
    ):
        styles = getSampleStyleSheet()
        style = styles["Normal"]
        style.fontName = label_font
        style.fontSize = label_font_size
        style.leading = label_font_size + 2

        line_height = style.leading
        flows = []

        def add_blanks():
            if print_blank_lines_above and blank_lines > 0:
                for _ in range(blank_lines):
                    flows.append(Spacer(1, line_height))

        add_blanks()
        flows.append(Paragraph(f"Name: {person_name}", style))

        add_blanks()
        signature_line = "_" * max(1, line_char_count_signature)
        flows.append(Paragraph(f"Signature: {signature_line}", style))

        add_blanks()
        date_line = "_" * max(1, line_char_count_date)
        flows.append(Paragraph(f"Date: {date_line}", style))

        flows.append(Spacer(1, line_height))  # small space after block
        return flows

    # ---------------------------------------------
    # Build ONE PAGE with MULTIPLE signature blocks
    # ---------------------------------------------
    def build_signature_page_bytes(
        person_names: list,
        blank_lines: int = 2,
        print_blank_lines_above: bool = True,
        landscape_mode: bool = False,
        margins_mm: float = 8.0,
        label_font: str = "Helvetica",
        label_font_size: float = 10.0,
        line_char_count_signature: int = 30,
        line_char_count_date: int = 10,
    ):
        """
        Returns bytes for a SINGLE-PAGE PDF that stacks all signature blocks vertically.
        """
        page_size = landscape(A4) if landscape_mode else A4
        buf = io.BytesIO()

        doc = SimpleDocTemplate(
            buf,
            pagesize=page_size,
            leftMargin=margins_mm * mm,
            rightMargin=margins_mm * mm,
            topMargin=margins_mm * mm,
            bottomMargin=margins_mm * mm,
        )

        elements = []
        for name in person_names:
            elements.extend(
                build_signature_block(
                    person_name=name,
                    blank_lines=blank_lines,
                    print_blank_lines_above=print_blank_lines_above,
                    label_font=label_font,
                    label_font_size=label_font_size,
                    line_char_count_signature=line_char_count_signature,
                    line_char_count_date=line_char_count_date,
                )
            )
            # No PageBreak — keep them on one page

        doc.build(elements)
        buf.seek(0)
        return buf.read()

    # ----------------------------
    # Compose and build a PDF file
    # ----------------------------
    def build_pdf(
        pdf_path,
        elements,
        landscape_mode: bool = True,
        margins_mm: float = 8.0,
    ):
        # Accept Path or str; ensure folder and convert to str for ReportLab
        pdf_path = Path(pdf_path)
        pdf_path.parent.mkdir(parents=True, exist_ok=True)

        page_size = landscape(A4) if landscape_mode else A4
        doc = SimpleDocTemplate(
            os.fspath(pdf_path),  # <-- convert Path -> str
            pagesize=page_size,
            leftMargin=margins_mm * mm,
            rightMargin=margins_mm * mm,
            topMargin=margins_mm * mm,
            bottomMargin=margins_mm * mm,
        )
        doc.build(elements)

    # -------------------------------------------
    # Append composite signature page(s) to a PDF
    # -------------------------------------------
    def append_signatures_to_pdf(
        input_pdf_path,
        person_names: list,
        output_pdf_path: str = None,
        copies: int = 1,
        blank_lines: int = 2,
        print_blank_lines_above: bool = True,
        landscape_mode: bool = False,
        margins_mm: float = 8.0,
        label_font: str = "Helvetica",
        label_font_size: float = 10.0,
        line_char_count_signature: int = 30,
        line_char_count_date: int = 10,
    ):
        """
        Appends one or more COMPOSITE signature pages (each containing all names stacked)
        to an existing PDF. If the input PDF doesn't exist, creates a new PDF consisting
        only of the composite signature pages.
        """
        input_pdf_path = Path(input_pdf_path)
        target_path = Path(output_pdf_path) if output_pdf_path else input_pdf_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        writer = PdfWriter()

        # If original exists, copy its pages
        if input_pdf_path.exists():
            reader = PdfReader(os.fspath(input_pdf_path))
            for page in reader.pages:
                writer.add_page(page)

        # Build a single composite signature page (stacked blocks)
        composite_bytes = build_signature_page_bytes(
            person_names=person_names,
            blank_lines=blank_lines,
            print_blank_lines_above=print_blank_lines_above,
            landscape_mode=landscape_mode,
            margins_mm=margins_mm,
            label_font=label_font,
            label_font_size=label_font_size,
            line_char_count_signature=line_char_count_signature,
            line_char_count_date=line_char_count_date,
        )

        # Append as many copies of the composite page as requested
        for _ in range(copies):
            sig_reader = PdfReader(io.BytesIO(composite_bytes))
            for page in sig_reader.pages:
                writer.add_page(page)

        # Write once AFTER appending
        with open(os.fspath(target_path), "wb") as f:
            writer.write(f)

    # ----------------------------
    # Build the table PDF first
    # ----------------------------
    table_flows = build_table_flowables(
        df=df,
        page_size=A4,
        landscape_mode=False,
        margins_mm=8.0,
        rows_per_page=50,
        notes_col_name="Notes",
        notes_weight=3.0,
        notes_max_ratio=0.50,
    )
    build_pdf(PDF_PATH, table_flows, landscape_mode=False, margins_mm=8.0)

    # ----------------------------
    # Collect signatories from config
    # ----------------------------
    person_names = []

    # Employees (only if employee_sig is true)
    if config.getboolean(f"customer.{cust}", "employee_sig", fallback=False):
        employees_raw = config.get(f"customer.{cust}", "employees", fallback="")
        employees = [e.strip() for e in employees_raw.split(",") if e.strip()]
        person_names.extend(employees)

    # Manager (only if manager_sig is true)
    if config.getboolean(f"customer.{cust}", "manager_sig", fallback=False):
        manager = config.get(f"customer.{cust}", "manager", fallback="").strip()
        if manager:
            person_names.append(manager)

    # ----------------------------
    # Append composite signature page
    # ----------------------------
    if len(person_names) > 0:
        append_signatures_to_pdf(
            input_pdf_path=PDF_PATH,
            person_names=person_names,   # <-- use the computed names
            copies=1,
            blank_lines=2,
            print_blank_lines_above=True,
            landscape_mode=False,
            margins_mm=8.0,
        )


# Example usage (replace df with your actual DataFrame)
if __name__ == "__main__":
    # Simple placeholder DF; replace with your real timesheet DF
    df = pd.DataFrame({
        "Date": ["2025-12-01", "2025-12-02"],
        "Task": ["Work", "Review"],
        "Hours": [8, 6],
        "Notes": ["Onsite", "Remote"]
    })
    build_cust_pdf("consumer", df)
