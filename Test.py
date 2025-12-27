def calculate_source_name(
    data: pd.DataFrame,
    lookups: dict,
    source_col: str = "Source"
) -> pd.Series:
    """
    Vectorised source-name calculation based on Source column.
    """

    if source_col not in data.columns:
        raise ValueError(f"Missing required column: {source_col}")

    source_name = pd.Series("", index=data.index, dtype="object")

    for source, func in SOURCE_FUNCTIONS.items():

        if source not in SOURCE_VALUE_COLUMNS:
            continue

        value_cols = SOURCE_VALUE_COLUMNS[source]

        # Validate required columns (only if needed)
        if value_cols:
            missing = [c for c in value_cols if c not in data.columns]
            if missing:
                raise ValueError(f"Missing columns for {source}: {missing}")

        mask = (
            data[source_col]
            .astype(str)
            .str.strip()
            .str.lower()
            == source.lower()
        )

        if not mask.any():
            continue

        # ---- CASE 1: No inputs, no lookup ----
        if not value_cols and source not in SOURCE_LOOKUP_KEYS:
            source_name.loc[mask] = [func() for _ in range(mask.sum())]
            continue

        # ---- CASE 2: Inputs only ----
        values = zip(*(data.loc[mask, c] for c in value_cols))

        if source not in SOURCE_LOOKUP_KEYS:
            source_name.loc[mask] = [func(*v) for v in values]
            continue

        # ---- CASE 3: Inputs + lookup ----
        lookup_key = SOURCE_LOOKUP_KEYS[source]
        lookup_dict = lookups.get(lookup_key, {})

        source_name.loc[mask] = [
            func(*v, mapping_lookup=lookup_dict) for v in values
        ]

    return source_name
    
