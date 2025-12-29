# connectors/call_usage_source.py

import pandas as pd
from processing.calculate_usage import USAGE_FUNCTIONS
from processing.calculate_source import SOURCE_FUNCTIONS


# ---------------- CONFIG ---------------- #

USAGE_VALUE_COLUMNS = {
    "Company Car": ["Business Distance"],
    "Hotel": ["Expense Type", "Cost"],
}

SOURCE_VALUE_COLUMNS = {
    "Company Car": ["Employee Country", "Expense Type", "Criteria Name"],
    "Private Car": ["Expense Type", "Criteria Name"],
    "Taxi": [],
}

USAGE_LOOKUP_KEYS = {
    "Company Car": ["distance_rate_lookup"],
    "Hotel": ["hotel_rate_lookup"],
}

SOURCE_LOOKUP_KEYS = {
    "Company Car": ["company_car_source"],
    "Private Car": ["private_car_source"],
}


# ---------------- SHARED HELPERS ---------------- #

def resolve_lookup_dicts(lookups: dict, lookup_keys: list[str]) -> dict:
    return {key: lookups.get(key, {}) for key in lookup_keys}


def _calculate_generic(
    data: pd.DataFrame,
    functions: dict,
    value_columns: dict,
    lookup_keys_map: dict,
    lookups: dict,
    source_col: str,
    dtype,
):
    result = pd.Series(None, index=data.index, dtype=dtype)

    for source, func in functions.items():
        cols = value_columns.get(source, [])

        missing = [c for c in cols if c not in data.columns]
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

        # ----- CASE 1: No inputs, no lookups -----
        if not cols and source not in lookup_keys_map:
            result.loc[mask] = [func() for _ in range(mask.sum())]
            continue

        # Extract row-wise values
        values = zip(*(data.loc[mask, c] for c in cols))

        # ----- CASE 2: Inputs only -----
        if source not in lookup_keys_map:
            result.loc[mask] = [func(*v) for v in values]
            continue

        # ----- CASE 3: Inputs + multiple lookups -----
        lookup_keys = lookup_keys_map[source]
        lookup_kwargs = resolve_lookup_dicts(lookups, lookup_keys)

        result.loc[mask] = [
            func(*v, **lookup_kwargs) for v in values
        ]

    return result


# ---------------- PUBLIC APIS ---------------- #

def calculate_usage(
    data: pd.DataFrame,
    lookups: dict,
    source_col: str = "Source",
) -> pd.Series:
    return _calculate_generic(
        data=data,
        functions=USAGE_FUNCTIONS,
        value_columns=USAGE_VALUE_COLUMNS,
        lookup_keys_map=USAGE_LOOKUP_KEYS,
        lookups=lookups,
        source_col=source_col,
        dtype="float64",
    )


def calculate_source_name(
    data: pd.DataFrame,
    lookups: dict,
    source_col: str = "Source",
) -> pd.Series:
    return _calculate_generic(
        data=data,
        functions=SOURCE_FUNCTIONS,
        value_columns=SOURCE_VALUE_COLUMNS,
        lookup_keys_map=SOURCE_LOOKUP_KEYS,
        lookups=lookups,
        source_col=source_col,
        dtype="object",
    )
