import numpy as np
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.formatting.rule import Rule
from openpyxl.styles.differential import DifferentialStyle


def compare_and_export_amount_diff(
    current_df,
    previous_df,
    key_col="Project Number",
    value_col="Approved Amount",
    diff_col="Amount_Diff",
    output_file="project_amount_diff_check.xlsx",
    sheet_name="Data",
    negative_color="F8D7DA",
    number_format="0.00%",
    max_col_width=40
):
    """
    Compare two datasets by aggregating a value column and exporting % difference to Excel

    Workflow:
    - Group + sum both datasets
    - Outer merge
    - Fill missing values
    - Calculate % diff
    - Sort
    - Export to Excel
    - Format + highlight negative diffs
    """

    # ------------------ 1) Aggregate ------------------
    cur_grp = (
        current_df
        .groupby(key_col, as_index=False)
        .agg({value_col: "sum"})
        .rename(columns={value_col: f"{value_col}_new"})
    )

    prev_grp = (
        previous_df
        .groupby(key_col, as_index=False)
        .agg({value_col: "sum"})
        .rename(columns={value_col: f"{value_col}_old"})
    )

    # ------------------ 2) Merge ------------------
    result = cur_grp.merge(
        prev_grp,
        on=key_col,
        how="outer"
    )

    # ------------------ 3) Clean ------------------
    result[[f"{value_col}_new", f"{value_col}_old"]] = (
        result[[f"{value_col}_new", f"{value_col}_old"]].fillna(0)
    )

    # ------------------ 4) Diff Calculation ------------------
    result[diff_col] = np.where(
        result[f"{value_col}_old"] == 0,
        1,  # 100% when previous is zero
        result[f"{value_col}_new"].div(result[f"{value_col}_old"]) - 1
    )

    # ------------------ 5) Sort ------------------
    result = result.sort_values(diff_col)

    # ------------------ 6) Export ------------------
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        result.to_excel(writer, index=False, sheet_name=sheet_name)

    # ------------------ 7) Excel Formatting ------------------
    wb = load_workbook(output_file)
    ws = wb[sheet_name]

    # Find diff column dynamically
    headers = [cell.value for cell in ws[1]]
    if diff_col not in headers:
        raise ValueError(f"Column '{diff_col}' not found in Excel sheet")

    col_idx = headers.index(diff_col) + 1
    col_letter = ws.cell(row=1, column=col_idx).column_letter

    max_row = ws.max_row
    diff_range = f"{col_letter}2:{col_letter}{max_row}"

    # Number format
    for row in range(2, max_row + 1):
        ws[f"{col_letter}{row}"].number_format = number_format

    # Conditional formatting (negative values)
    fill = PatternFill(
        start_color=negative_color,
        end_color=negative_color,
        fill_type="solid"
    )
    dxf = DifferentialStyle(fill=fill)

    rule = Rule(
        type="expression",
        dxf=dxf,
        formula=[f"{col_letter}2<0"]
    )

    ws.conditional_formatting.add(diff_range, rule)

    # Freeze header
    ws.freeze_panes = "A2"

    # Auto-size columns
    for col in ws.columns:
        max_length = 0
        col_letter = col[0].column_letter

        for cell in col:
            try:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            except:
                pass

        ws.column_dimensions[col_letter].width = min(max_length + 2, max_col_width)

    # Save
    wb.save(output_file)

    print(f"Saved: {output_file}")

    return result
        
result = compare_and_export_amount_diff(
    current_df=data,
    previous_df=prev_data,
    key_col="Project Number",
    value_col="Approved Amount",
    output_file="project_amount_diff_check.xlsx"
)
