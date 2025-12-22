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
