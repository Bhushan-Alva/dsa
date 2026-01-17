import pandas as pd

def fast_export_excel(df, file_path, max_col_width=40, min_col_width=12, sample_rows=200):
    """
    Fast Excel writer using xlsxwriter
    - Styles header
    - Freezes header row
    - Auto-fits columns using header + sample rows (not full scan)
    """

    with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)

        workbook = writer.book
        worksheet = writer.sheets["Sheet1"]

        # ======================
        # Header format
        # ======================
        header_format = workbook.add_format({
            "bold": True,
            "text_wrap": True,
            "valign": "middle",
            "align": "center",
            "fg_color": "#4F81BD",
            "font_color": "white",
            "border": 1
        })

        # Rewrite headers with format
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(0, col_num, col_name, header_format)

        # Freeze header
        worksheet.freeze_panes(1, 0)

        # ======================
        # Fast auto-fit
        # ======================
        for col_num, col_name in enumerate(df.columns):
            max_length = len(str(col_name))

            # Sample only first N rows (MUCH faster than full scan)
            col_series = df[col_name].head(sample_rows).astype(str)

            max_sample = col_series.map(len).max()
            max_length = max(max_length, max_sample)

            adjusted_width = min(
                max(max_length + 2, min_col_width),
                max_col_width
            )

            worksheet.set_column(col_num, col_num, adjusted_width)
            
