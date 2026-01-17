import numpy as np
import pandas as pd


# ---------- Helpers ----------

def safe_lower(x):
    """Lowercase only if x is a valid non-empty string, else return np.nan"""
    if isinstance(x, str) and x.strip():
        return x.lower()
    return np.nan


def safe_float(x):
    """Convert to float if possible, else return np.nan"""
    try:
        if pd.isna(x):
            return np.nan
        return float(x)
    except:
        return np.nan


# ---------- Main Function ----------

def taxi_usage(
    country_of_transaction: str,
    city_of_transaction: str,
    approved_amount: float,
    **lookups
):
    """
    Calculates taxi usage based on:
    - City+Country rates (preferred)
    - Country-only fallback
    - Start rate subtraction
    - Per-km division
    - +2 adjustment
    - Preserves original sign
    """

    # ---- Normalize inputs ----
    city = safe_lower(city_of_transaction)
    country = safe_lower(country_of_transaction)

    # ---- Lookups ----
    normalized_city = lookups["taxi_city_normalized_mapping"].get(
        f"{country}{city}", np.nan
    )
    normalized_city = safe_lower(normalized_city)

    city_start_rate = lookups["taxi_city_start_rate_mapping"].get(
        f"{country}{normalized_city}", np.nan
    )
    country_start_rate = lookups["taxi_country_start_rate_mapping"].get(
        country, np.nan
    )

    city_per_km_rate = lookups["taxi_city_1km_rate_mapping"].get(
        f"{country}{normalized_city}", np.nan
    )
    country_per_km_rate = lookups["taxi_country_1km_rate_mapping"].get(
        country, np.nan
    )

    # ---- Sanitize numeric values ----
    city_start_rate = safe_float(city_start_rate)
    city_per_km_rate = safe_float(city_per_km_rate)
    country_start_rate = safe_float(country_start_rate)
    country_per_km_rate = safe_float(country_per_km_rate)

    # ---- Zero check ----
    if approved_amount == 0 or pd.isna(approved_amount):
        return 0

    # ---- Sign handling ----
    mul = -1 if approved_amount < 0 else 1
    approved_amount = abs(approved_amount)

    # ---- Choose city or country rates ----
    if pd.isna(city_start_rate) or pd.isna(city_per_km_rate):
        start_rate = country_start_rate
        per_km_rate = country_per_km_rate
    else:
        start_rate = city_start_rate
        per_km_rate = city_per_km_rate

    # ---- Final safety check ----
    if pd.isna(start_rate) or pd.isna(per_km_rate) or per_km_rate == 0:
        return 0

    # ---- Core math ----
    usage = ((approved_amount - start_rate) / per_km_rate) + 2

    # Optional: clamp minimum usage to 2
    # usage = max(2, usage)

    return usage * mul
        
