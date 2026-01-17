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
# EXCEL BEAUTIFIER
# ==================================

def beautify_excel(
    file_path,
    header_fill_color="4F81BD",
    header_font_color="FFFFFF",
    max_col_width=40,
    min_col_width=12,
    freeze_header=True
):
    wb = load_workbook(file_path)
    ws = wb.active

    # Header style
    header_font = Font(bold=True, color=header_font_color)
    header_fill = PatternFill("solid", fgColor=header_fill_color)
    header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

    for cell in ws[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align

    # Freeze header
    if freeze_header:
        ws.freeze_panes = "A2"

    # Auto-fit columns
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            try:
                val = str(cell.value) if cell.value is not None else ""
                max_length = max(max_length, len(val))
            except:
                pass

        adjusted_width = min(
            max(max_length + 2, min_col_width),
            max_col_width
        )

        ws.column_dimensions[col_letter].width = adjusted_width

    # Align numeric columns right
    numeric_cols = {"Usage", "Cost", "Number2", "Number3"}

    header_map = {
        cell.value: cell.column_letter
        for cell in ws[1]
    }

    for col_name in numeric_cols:
        if col_name in header_map:
            col_letter = header_map[col_name]
            for cell in ws[col_letter][1:]:
                cell.alignment = Alignment(horizontal="right")

    wb.save(file_path)


# ==================================
# CORE LOGIC
# ==================================

def build_output_for_source(df, source, output_map, source_col="Source Name"):
    df = df.copy()

    final_cols = output_map["Common Columns"] + output_map.get(source, [])

    # Ensure all required columns exist
    for col in final_cols:
        if col not in df.columns:
            df[col] = ""

    # Filter source
    df = df[df[source_col] == source]

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

    out_df = (
        df
        .groupby("Console Key", as_index=False)
        .agg(agg_rules)
    )

    return out_df[final_cols]


def export_sources_to_excel(df, output_map, output_dir, source_col="Source Name"):
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
        file_path = os.path.join(output_dir, filename)

        # Write Excel
        out_df.to_excel(file_path, index=False)

        # Beautify Excel
        beautify_excel(file_path)

        print(f"Saved & beautified: {file_path}")


# ==================================
# RUN PIPELINE
# ==================================

if __name__ == "__main__":
    # Load your raw data
    raw_df = pd.read_excel("raw_expense_data.xlsx")

    # Export per source (beautified)
    export_sources_to_excel(
        df=raw_df,
        output_map=output_columns,
        output_dir="expense_outputs"
    )
