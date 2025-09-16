import os
import pandas as pd

RAW_DIR   = r"01. Raw"
TRANS_DIR = r"02. Raw - Translated"
CONS_FILE = r"03. Consolidated/consolidated.xlsx"
OUTPUT    = "column_check_summary.xlsx"

def column_info_by_position(df):
    """
    Return [(position, header_lowercase, non-null count)]
    """
    return [(i, col.lower(), df[col].notna().sum()) for i, col in enumerate(df.columns)]

def safe_read(path):
    try:
        df = pd.read_excel(path, dtype=str)
        # force all column names to lowercase
        df.columns = [c.lower() for c in df.columns]
        return df
    except Exception as e:
        print(f"Error reading {path}: {e}")
        return None

# Read consolidated once
cons_df = safe_read(CONS_FILE)
if cons_df is None:
    raise SystemExit("Cannot read consolidated file.")
cons_first_col = cons_df.columns[0]  # first column = source filename

rows = []

for fname in os.listdir(RAW_DIR):
    if not fname.lower().endswith((".xls", ".xlsx")):
        continue

    fname_lower = fname.lower()
    raw_path  = os.path.join(RAW_DIR, fname)
    trans_path = os.path.join(
        TRANS_DIR,
        fname.replace(".xlsx", " - translated.xlsx")
    )

    raw_df  = safe_read(raw_path)
    trans_df = safe_read(trans_path)
    if raw_df is None or trans_df is None:
        continue

    # filter consolidated rows where first column (lowercase) equals filename (lowercase)
    cons_sub = cons_df[cons_df[cons_first_col].str.lower() == fname_lower]

    for pos, raw_head, raw_count in column_info_by_position(raw_df):

        # translated: match by position
        if pos < trans_df.shape[1]:
            t_head = trans_df.columns[pos].lower()
            t_count = trans_df.iloc[:, pos].notna().sum()
        else:
            t_head = t_count = None

        # consolidated: use translated header + filename filter
        if t_head and t_head in cons_sub.columns:
            c_count = cons_sub[t_head].notna().sum()
        else:
            c_count = None

        diff_raw_trans = (
            None if (raw_count is None or t_count is None)
            else raw_count - t_count
        )
        diff_trans_cons = (
            None if (t_count is None or c_count is None)
            else t_count - c_count
        )

        rows.append({
            "file name": fname_lower,
            "position": pos,
            "raw header": raw_head,
            "raw count": raw_count,
            "translated header": t_head,
            "translated count": t_count,
            "consolidated count": c_count,
            "diff raw-trans": diff_raw_trans,
            "diff trans-cons": diff_trans_cons
        })

summary = pd.DataFrame(rows)
summary.to_excel(OUTPUT, index=False)
print(f"Summary written to {OUTPUT}")
