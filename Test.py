def convert_numeric(series):
    return (
        series
        .astype(str)
        .str.replace(",", "", regex=False)
        .replace({"": pd.NA, "nan": pd.NA})
        .pipe(pd.to_numeric, errors="coerce")
    )
    
    
    def apply_type_mapping(df, dtype_mapping):
    for col, dtype in dtype_mapping.items():

        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

        dtype = dtype.lower()

        # ---- Datetime ----
        if dtype.startswith("datetime"):
            df[col] = pd.to_datetime(df[col], errors="coerce")

        # ---- Float ----
        elif dtype in ("float", "float64"):
            df[col] = convert_numeric(df[col])

        # ---- Integer (nullable!) ----
        elif dtype in ("int", "int64"):
            df[col] = convert_numeric(df[col]).astype("Int64")

        # ---- String (NA-safe) ----
        elif dtype in ("str", "string"):
            df[col] = df[col].astype("string")

        # ---- Boolean (NA-safe) ----
        elif dtype in ("bool", "boolean"):
            df[col] = df[col].astype("boolean")

        # ---- Fallback ----
        else:
            df[col] = df[col].astype(dtype)

    return df
    
