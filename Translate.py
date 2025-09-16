import os
import pandas as pd

RAW_DIR   = r"01. Raw"
TRANS_DIR = r"02. Raw - Translated"
CONS_FILE = r"03. Consolidated/consolidated.xlsx"
OUTPUT    = "column_check_summary.xlsx"

def column_info_by_position(df):
    """Return [(pos, header, non-null count)]"""
    return [(i, col, df[col].notna().sum()) for i, col in enumerate(df.columns)]

def safe_read(path):
    try:
        return pd.read_excel(path, dtype=str)
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

# read consolidated once
cons_df = safe_read(CONS_FILE)
if cons_df is None:
    raise SystemExit("Cannot read consolidated file.")

consolidated_first_col = cons_df.columns[0]  # first column = source filename

rows = []

for fname in os.listdir(RAW_DIR):
    if not fname.lower().endswith((".xls", ".xlsx")):
        continue

    raw_path = os.path.join(RAW_DIR, fname)
    trans_path = os.path.join(TRANS_DIR, fname.replace(".xlsx", " - translated.xlsx"))

    raw_df = safe_read(raw_path)
    trans_df = safe_read(trans_path)
    if raw_df is None or trans_df is None:
        continue

    # rows in consolidated belonging to this source file
    cons_sub = cons_df[cons_df[consolidated_first_col] == fname]

    for pos, raw_head, raw_count in column_info_by_position(raw_df):
        # translated compare by position
        if pos < trans_df.shape[1]:
            t_head = trans_df.columns[pos]
            t_count = trans_df.iloc[:, pos].notna().sum()
        else:
            t_head = t_count = None

        # consolidated compare by column name (same names but maybe different order)
        if raw_head in cons_sub.columns:
            c_head = raw_head
            c_count = cons_sub[raw_head].notna().sum()
        else:
            c_head = c_count = None

        rows.append({
            "File Name": fname,
            "Position": pos,
            "Raw Header": raw_head,
            "Raw Count": raw_count,
            "Translated Header": t_head,
            "Translated Count": t_count,
            "Consolidated Header": c_head,
            "Consolidated Count": c_count
        })

summary = pd.DataFrame(rows)
summary.to_excel(OUTPUT, index=False)
print(f"Summary written to {OUTPUT}")
