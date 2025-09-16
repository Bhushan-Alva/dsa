import os
import pandas as pd

RAW_DIR   = r"01. Raw"
TRANS_DIR = r"02. Raw - Translated"
CONS_FILE = r"03. Consolidated/consolidated.xlsx"
OUTPUT    = "column_check_summary.xlsx"

def column_info_by_position(df):
    """[(position, header, non-null count)]"""
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
cons_first_col = cons_df.columns[0]  # first column is the source filename

rows = []

for fname in os.listdir(RAW_DIR):
    if not fname.lower().endswith((".xls", ".xlsx")):
        continue

    raw_path  = os.path.join(RAW_DIR, fname)
    trans_path = os.path.join(TRANS_DIR,
                              fname.replace(".xlsx", " - translated.xlsx"))

    raw_df  = safe_read(raw_path)
    trans_df = safe_read(trans_path)
    if raw_df is None or trans_df is None:
        continue

    # Subset of consolidated rows for this source file
    cons_sub = cons_df[cons_df[cons_first_col] == fname]

    for pos, raw_head, raw_count in column_info_by_position(raw_df):

        # translated compare by position
        if pos < trans_df.shape[1]:
            t_head = trans_df.columns[pos]
            t_count = trans_df.iloc[:, pos].notna().sum()
        else:
            t_head = t_count = None

        # consolidated count: use translated header + filename filter
        if t_head in cons_sub.columns:
            c_count = cons_sub[t_head].notna().sum()
        else:
            c_count = None

        # differences
        diff_raw_trans = (
            None if (raw_count is None or t_count is None)
            else raw_count - t_count
        )
        diff_trans_cons = (
            None if (t_count is None or c_count is None)
            else t_count - c_count
        )

        rows.append({
            "File Name": fname,
            "Position": pos,
            "Raw Header": raw_head,
            "Raw Count": raw_count,
            "Translated Header": t_head,
            "Translated Count": t_count,
            "Consolidated Count": c_count,
            "Diff Raw-Trans": diff_raw_trans,
            "Diff Trans-Cons": diff_trans_cons
        })

summary = pd.DataFrame(rows)
summary.to_excel(OUTPUT, index=False)
print(f"Summary written to {OUTPUT}")
