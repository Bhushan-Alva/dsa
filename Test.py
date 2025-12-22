"""
    Build a normalized lookup key by concatenating columns.

    Parameters
    ----------
    df : pd.DataFrame
        Source dataframe
    cols : list[str]
        Columns to concatenate
    sep : str, optional
        Separator between values (default: "")
    lower : bool, optional
        Convert key to lowercase (default: True)

    Returns
    -------
    pd.Series
        Normalized lookup key
    """

def calculate_usage(data: pd.DataFrame, source_col="Source") -> pd.Series:
    """
    Vectorised usage calculation based on Source column.
    """

    if source_col not in data.columns:
        raise ValueError(f"Missing required column: {source_col}")

    usage = pd.Series(index=data.index, dtype="float64")

    for source, func in SOURCE_FUNCTIONS.items():
        if source not in SOURCE_COLUMN_MAPPING:
            continue

        cols = SOURCE_COLUMN_MAPPING[source]

        # Validate required columns
        missing = [c for c in cols if c not in data.columns]
        if missing:
            raise ValueError(f"Missing columns for {source}: {missing}")

        mask = data[source_col].str.lower() == source

        if not mask.any():
            continue

        # Extract values column-wise and call pure function row-wise via zip
        values = zip(*(data.loc[mask, c] for c in cols))

        usage.loc[mask] = [
            func(*v) for v in values
        ]

    return usage
        
