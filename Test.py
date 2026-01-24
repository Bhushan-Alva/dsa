import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.formatting.rule import Rule
from openpyxl.styles.differential import DifferentialStyle


def duplicate_check_export(
    df,
    columns,
    output_file,
    sheet_name="Data",
    highlight_color="FFF3CD",
    max_col_width=40
):
    """
    Reusable duplicate checker and Excel exporter

    Parameters
    ----------
    df : pandas.DataFrame
        Source dataframe
    columns : list
        Columns to include in output
        First column is used for duplicate highlighting
    output_file : str
        Excel file name to save
    sheet_name : str
        Excel sheet name
    highlight_color : str
        Hex fill color for duplicates
    max_col_width : int
        Maximum Excel column width
    """

    # ------------------ 1) Filter + Deduplicate ------------------
    df_out = df[columns].drop_duplicates()

    # ------------------ 2) Export to Excel ------------------
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df_out.to_excel(writer, index=False, sheet_name=sheet_name)

    # ------------------ 3) Open with openpyxl ------------------
    wb = load_workbook(output_file)
    ws = wb[sheet_name]

    # ------------------ 4) Highlight Duplicates in Column A ------------------
    max_row = ws.max_row
    cell_range = f"A2:A{max_row}"

    fill = PatternFill(
        start_color=highlight_color,
        end_color=highlight_color,
        fill_type="solid"
    )
    dxf = DifferentialStyle(fill=fill)

    rule = Rule(type="duplicateValues", dxf=dxf)
    ws.conditional_formatting.add(cell_range, rule)

    # ------------------ 5) Freeze Header ------------------
    ws.freeze_panes = "A2"

    # ------------------ 6) Auto-size Columns ------------------
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

    # ------------------ 7) Save ------------------
    wb.save(output_file)

    # ------------------ 8) Console Status ------------------
    first_col = columns[0]
    if df_out.shape[0] == len(df_out[first_col].drop_duplicates()):
        print(f"Saved: {output_file}")
        print("No Duplicate records found")
    else:
        print(f"Saved: {output_file}")
        print("Duplicate records found")

    return df_out
