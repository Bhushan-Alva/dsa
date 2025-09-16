import os
import pandas as pd

RAW_DIR = r"01. Raw"
TRANS_DIR = r"02. Raw - Translated"
CONS_DIR = r"03. Consolidated"
OUTPUT   = "column_check_summary.xlsx"

def column_info_by_position(df):
    """Return list of (position, header, count_non_null)"""
    return [(i, col, df[col].notna().sum()) for i, col in enumerate(df.columns)]

def load_file(path):
    try:
        return pd.read_excel(path, dtype=str)   # treat all as str
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

rows = []

for fname in os.listdir(RAW_DIR):
    if not fname.lower().endswith(('.xls', '.xlsx')): 
        continue

    raw_path  = os.path.join(RAW_DIR, fname)
    trans_path = os.path.join(TRANS_DIR, fname.replace('.xlsx',' - translated.xlsx'))
    cons_path  = os.path.join(CONS_DIR, fname)

    raw_df  = load_file(raw_path)
    trans_df = load_file(trans_path)
    cons_df  = load_file(cons_path)

    if raw_df is None or trans_df is None or cons_df is None:
        continue

    # Compare by column index
    for i, (pos, raw_head, raw_count) in enumerate(column_info_by_position(raw_df)):
        # translated: match by position
        if i < trans_df.shape[1]:
            t_head = trans_df.columns[i]
            t_count = trans_df.iloc[:, i].notna().sum()
        else:
            t_head = t_count = None

        # consolidated: match by name (same names but possibly different order)
        if raw_head in cons_df.columns:
            c_head = raw_head
            c_count = cons_df[raw_head].notna().sum()
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

summary_df = pd.DataFrame(rows)
summary_df.to_excel(OUTPUT, index=False)
print(f"Summary written to {OUTPUT}")
