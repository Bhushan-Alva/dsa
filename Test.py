import pandas as pd

def build_console_key_vectorized(df, source_col, key_map, sep="|"):
    df = df.copy()
    df["console_key"] = ""

    # Collect all possible key columns
    all_cols = set(col for cols in key_map.values() for col in cols)

    # Normalize once
    for col in all_cols:
        if col not in df.columns:
            df[col] = ""

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Build per source
    for source, cols in key_map.items():
        if not cols:
            continue

        mask = df[source_col].eq(source)
        if not mask.any():
            continue

        df.loc[mask, "console_key"] = (
            df.loc[mask, cols]
              .agg(sep.join, axis=1)
        )

    return df
