# ================================
# SOURCE-AWARE REPORTING ENGINE
# (CREATES + ATTACHES EXCEL)
# ================================

import os
import numpy as np
import pandas as pd
import win32com.client as win32


# -------------------------------------------------
# 1) BUILD COUNTRY x MONTH % DIFFERENCE MATRIX
# -------------------------------------------------
def build_pct_diff_matrix(
    latest_raw: pd.DataFrame,
    old_raw: pd.DataFrame,
    country_col="Employee Country",
    date_col="Report Extract Date",
    value_col="Approved Amount"
):
    month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

    latest = latest_raw.copy()
    old = old_raw.copy()

    latest["Month"] = latest[date_col].dt.strftime("%b")
    old["Month"] = old[date_col].dt.strftime("%b")

    latest_months = pd.Series(latest["Month"]).dropna().astype(str).tolist()
    valid_latest_months = [m for m in month_order if m in set(latest_months)]
    latest_month_name = valid_latest_months[-1] if valid_latest_months else None

    latest_grp = (
        latest
        .groupby([country_col, "Month"], as_index=False)[value_col]
        .sum()
    )

    old_grp = (
        old
        .groupby([country_col, "Month"], as_index=False)[value_col]
        .sum()
    )

    comparison = (
        pd.merge(
            latest_grp,
            old_grp,
            on=[country_col, "Month"],
            how="outer",
            suffixes=("_latest", "_old")
        )
        .fillna(0.0)
    )

    latest_vals = comparison[f"{value_col}_latest"]
    old_vals = comparison[f"{value_col}_old"]

    comparison["Pct_Difference"] = np.where(
        old_vals == 0,
        np.where(latest_vals == 0, 0.0, np.sign(latest_vals) * 100.0),
        ((latest_vals - old_vals) / old_vals) * 100.0
    ).round(2)

    matrix_view = (
        comparison
        .pivot_table(
            index=country_col,
            columns="Month",
            values="Pct_Difference",
            aggfunc="first",
            fill_value=0.0
        )
        .reindex(columns=month_order)
    )

    return matrix_view, latest_month_name


# -------------------------------------------------
# 2) SAVE MATRIX TO EXCEL
# -------------------------------------------------
def save_matrix_to_excel(matrix_df, excel_path, sheet_name="Difference"):
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)

    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        matrix_df.to_excel(writer, sheet_name=sheet_name)

    return excel_path


# -------------------------------------------------
# 3) RENDER OUTLOOK-SAFE HTML TABLE
# -------------------------------------------------
def render_html_matrix(df: pd.DataFrame, latest_month_name: str) -> str:
    RED = "#FFD5D5"
    BLUE = "#CFE8FF"
    GREEN = "#C6EFCE"

    table_style = (
        "border-collapse: collapse; "
        "font-family: Segoe UI, Roboto, Arial; "
        "font-size: 12px;"
    )

    cell_style = "border: 1px solid #bbb; padding: 6px 8px; text-align: center;"
    row_header_style = cell_style + " text-align: left; font-weight: bold;"

    html = [f'<table style="{table_style}">']

    # Header
    html.append("<thead><tr>")
    html.append(f'<th style="{cell_style}"></th>')
    for col in df.columns:
        html.append(f'<th style="{cell_style}">{col}</th>')
    html.append("</tr></thead>")

    # Body
    html.append("<tbody>")
    for idx, row in df.iterrows():
        html.append("<tr>")
        html.append(f'<th style="{row_header_style}">{idx}</th>')

        for col in df.columns:
            val = row[col]

            if pd.isna(val):
                disp = "NA"
                style = cell_style
            else:
                val = float(val)
                disp = f"{val:.2f}"
                is_zero = abs(val) < 1e-12

                if latest_month_name and col == latest_month_name:
                    bg = RED if is_zero else BLUE
                else:
                    bg = GREEN if is_zero else RED

                style = f"{cell_style} background-color: {bg};"

            html.append(f'<td style="{style}">{disp}</td>')

        html.append("</tr>")
    html.append("</tbody></table>")

    return "\n".join(html)


# -------------------------------------------------
# 4) SEND EMAIL VIA OUTLOOK
# -------------------------------------------------
def send_outlook_email(
    to_emails,
    subject,
    message,
    html_table,
    excel_path=None,
    cc_emails=None,
    bcc_emails=None,
    preview=False
):
    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)

    mail.To = "; ".join(to_emails)

    if cc_emails:
        mail.CC = "; ".join(cc_emails)

    if bcc_emails:
        mail.BCC = "; ".join(bcc_emails)

    mail.Subject = subject

    html_body = f"""
    <html>
    <body style="font-family: Segoe UI, Roboto, Arial; font-size: 14px;">
        <pre style="white-space: pre-wrap; margin: 0 0 12px 0;">{message.strip()}</pre>
        {html_table}
    </body>
    </html>
    """

    mail.HTMLBody = html_body

    if excel_path and os.path.exists(excel_path):
        mail.Attachments.Add(Source=excel_path)

    if preview:
        mail.Display()
    else:
        mail.Send()

    print(f"Email sent: {subject}")


# -------------------------------------------------
# 5) SOURCE-AWARE PIPELINE RUNNER
# -------------------------------------------------
def run_country_month_report_by_source(
    latest_raw,
    old_raw,
    source_col="Source",
    output_dir="reports",
    to_emails=None,
    subject_prefix="MyExpense Company Car",
    custom_message="",
    cc_emails=None,
    preview=True
):
    """
    Generates:
    - One Excel file per Source
    - One Email per Source (with Excel attached)

    Returns:
        dict[source] = matrix_view
    """

    if to_emails is None:
        raise ValueError("to_emails must be provided")

    results = {}

    sources = (
        pd.concat([latest_raw[source_col], old_raw[source_col]])
        .dropna()
        .unique()
    )

    for src in sources:
        latest_src = latest_raw[latest_raw[source_col] == src]
        old_src = old_raw[old_raw[source_col] == src]

        if latest_src.empty and old_src.empty:
            continue

        matrix, latest_month = build_pct_diff_matrix(
            latest_src,
            old_src
        )

        # Create Excel file
        safe_src = str(src).replace(" ", "_").replace("/", "_")
        excel_path = os.path.join(output_dir, f"Difference_{safe_src}.xlsx")
        save_matrix_to_excel(matrix, excel_path)

        # Create HTML table
        html_table = render_html_matrix(matrix, latest_month)

        # Send mail
        subject = f"{subject_prefix} - {src} - Country x Month % Difference"

        send_outlook_email(
            to_emails=to_emails,
            cc_emails=cc_emails,
            subject=subject,
            message=custom_message,
            html_table=html_table,
            excel_path=excel_path,
            preview=preview
        )

        results[src] = matrix

    return results


# -------------------------------------------------
# 6) EXAMPLE USAGE
# -------------------------------------------------
# matrices = run_country_month_report_by_source(
#     latest_raw=latest_raw_df,
#     old_raw=old_raw_df,
#     source_col="Source",
#     output_dir="C:/Users/BHALVA/Reports",
#     to_emails=["bhushan.alva@capgemini.com"],
#     cc_emails=["cat_myexpense.in@capgemini.com"],
#     subject_prefix="MyExpense Company Car",
#     custom_message="""
# Hello All,
#
# This is the automated Country x Month % Difference report.
# Please find the Excel attached for detailed analysis.
#
# Thanks,
# """,
#     preview=True   # False = auto-send
# )
