import os
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

# ==================================
# CONFIG — OUTPUT SCHEMA
# ==================================

output_columns = {
    "Common Columns": [
        "Accounting Date", "Chargeable/Non-Chargeable", "Console Key",
        "Cost", "Currency", "Description/Notes", "Emp BU Code",
        "Emp BU Label - Lookup Key", "Emp GBL ID", "Employee First Name",
        "Employee Last Name", "Employee Project ID", "Legal Entity",
        "Long Text 1", "Long Text 2", "Market Unit", "Project Details",
        "Project Unit", "Service Line", "Source Name",
        "To be uploaded?", "Travel Category", "Travel Purpose",
        "Usage", "Usage Unit Input", "Employee Grade", "Text3",
        "Departure Date", "Arrival Date"
    ],

    "Company Car": ["Text2", "Text3", "Employee Legal Unit"],
    "Private Car": ["Text2", "Text3", "Employee Grade"],
    "Rental Car": ["Text2", "Text3"],
    "LPT": ["Text5", "Number2"],
    "Taxi": ["Country of Transaction", "City Name", "Text3", "Text5", "Number2", "Number3"],
    "Rail": ["Text1", "Text3", "Country of Transaction", "Emissions"],
}

# ==================================
# HELPERS
# ==================================

def get_sources(df, source_col="Source Name"):
    """Return unique source names in dataset"""
    return (
        df[source_col]
        .dropna()
        .astype(str)
        .unique()
    )


def build_filename(df, source, date_col="Accounting Date", source_col="Source Name"):
    """
    Format:
    2025 01-12 Consolidated Taxi.xlsx
    """
    src_df = df[df[source_col] == source]
    dates = pd.to_datetime(src_df[date_col], errors="coerce")

    if dates.notna().any():
        max_date = dates.max()
        year = max_date.year
        month = f"{max_date.month:02d}"
    else:
        year = "UNKNOWN"
        month = "00"

    safe_source = (
        source
        .replace("/", "_")
        .replace("\\", "_")
    )

    return f"{year} 01-{month} Consolidated {safe_source}.xlsx"


# ==================================
# CORE LOGIC
# ==================================

def build_output_for_source(df, source, output_map, source_col="Source Name"):
    """
    Rules:
    - Group by Console Key
    - Usage & Cost = SUM
    - Other columns = FIRST non-null
    - Missing columns = BLANK
    """

    df = df.copy()

    # Final schema
    final_cols = output_map["Common Columns"] + output_map.get(source, [])

    # Ensure all required columns exist
    for col in final_cols:
        if col not in df.columns:
            df[col] = ""

    # Filter source rows
    df = df[df[source_col] == source]

    # Return empty schema if no data
    if df.empty:
        return pd.DataFrame(columns=final_cols)

    # Numeric safety
    df["Usage"] = pd.to_numeric(df["Usage"], errors="coerce").fillna(0)
    df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce").fillna(0)

    # Aggregation rules
    agg_rules = {}
    for col in final_cols:
        if col in ["Usage", "Cost"]:
            agg_rules[col] = "sum"
        else:
            agg_rules[col] = lambda x: x.dropna().iloc[0] if not x.dropna().empty else ""

    # Group + Aggregate
    out_df = (
        df
        .groupby("Console Key", as_index=False)
        .agg(agg_rules)
    )

    return out_df[final_cols]


# ==================================
# FAST CSV → XLSX BEAUTIFIER
# ==================================

def csv_to_beautified_xlsx_fixed_width(csv_path, xlsx_path, col_width=30):
    """
    Ultra-fast:
    - Reads CSV
    - Writes XLSX
    - Styles header only
    - Sets ALL column widths to fixed value
    """

    # Convert CSV → XLSX
    df = pd.read_csv(csv_path, low_memory=False)
    df.to_excel(xlsx_path, index=False)

    # Light formatting
    wb = load_workbook(xlsx_path)
    ws = wb.active

    # Header style
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="4F81BD")
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align

    # Freeze header
    ws.freeze_panes = "A2"

    # Fixed width for ALL columns
    for col in range(1, ws.max_column + 1):
        col_letter = ws.cell(row=1, column=col).column_letter
        ws.column_dimensions[col_letter].width = col_width

    wb.save(xlsx_path)


# ==================================
# EXPORT ORCHESTRATOR
# ==================================

def export_sources_to_excel_fast(df, output_map, output_dir, source_col="Source Name"):
    """
    Pipeline:
    - Build output per source
    - Write CSV (FAST)
    - Convert CSV → Beautified XLSX (FAST)
    - Delete CSV
    """

    os.makedirs(output_dir, exist_ok=True)

    sources = get_sources(df, source_col)
    print(f"Found sources: {list(sources)}")

    for source in sources:
        print(f"Processing: {source}")

        out_df = build_output_for_source(
            df=df,
            source=source,
            output_map=output_map,
            source_col=source_col
        )

        filename = build_filename(df, source, source_col=source_col)

        xlsx_path = os.path.join(output_dir, filename)
        csv_path = xlsx_path.replace(".xlsx", ".csv")

        # STEP 1 — FAST CSV WRITE
        out_df.to_csv(csv_path, index=False)
        print(f"CSV written: {csv_path}")

        # STEP 2 — FAST CSV → XLSX + BEAUTIFY
        csv_to_beautified_xlsx_fixed_width(
            csv_path=csv_path,
            xlsx_path=xlsx_path,
            col_width=30
        )
        print(f"Beautified XLSX: {xlsx_path}")

        # STEP 3 — CLEANUP
        os.remove(csv_path)


# ==================================
# RUN PIPELINE
# ==================================

if __name__ == "__main__":
    # Load your raw data
    raw_df = pd.read_excel("raw_expense_data.xlsx")

    # Export per source (FAST, BEAUTIFIED)
    export_sources_to_excel_fast(
        df=raw_df,
        output_map=output_columns,
        output_dir="expense_outputs"
    )
    
