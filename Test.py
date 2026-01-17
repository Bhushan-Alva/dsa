import os
import pandas as pd

# ==============================
# CONFIG
# ==============================

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


# ==============================
# CORE FUNCTIONS
# ==============================

def get_sources(df, source_col="Source Name"):
    """Return unique source names from dataset"""
    return (
        df[source_col]
        .dropna()
        .astype(str)
        .unique()
    )


def build_output_for_source(df, source, output_map, source_col="Source Name"):
    """
    Builds aggregated output dataframe for ONE source

    Rules:
    - Group by Console Key
    - Usage & Cost = SUM
    - Other columns = FIRST non-null
    - Missing columns = BLANK
    """

    df = df.copy()

    # Final schema for this source
    final_cols = output_map["Common Columns"] + output_map.get(source, [])

    # Ensure all columns exist
    for col in final_cols:
        if col not in df.columns:
            df[col] = ""

    # Filter source rows
    df = df[df[source_col] == source]

    # Return empty file with schema if no data
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


def export_sources_to_excel(df, output_map, output_dir, source_col="Source Name"):
    """
    Creates ONE EXCEL FILE PER SOURCE
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

        # Safe file name
        safe_name = (
            source
            .replace(" ", "_")
            .replace("/", "_")
            .replace("\\", "_")
        )

        file_path = os.path.join(
            output_dir,
            f"{safe_name}_output.xlsx"
        )

        out_df.to_excel(file_path, index=False)
        print(f"Saved: {file_path}")


# ==============================
# RUN PIPELINE
# ==============================

if __name__ == "__main__":
    # Example: Load your raw data
    raw_df = pd.read_excel("raw_expense_data.xlsx")

    # Export one Excel per source
    export_sources_to_excel(
        df=raw_df,
        output_map=output_columns,
        output_dir="expense_outputs"
    )
    
