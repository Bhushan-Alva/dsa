def add_rental_report_flags(df: pd.DataFrame) -> pd.DataFrame:
    exp_type_norm = (
        df["Expense Type"]
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    total = df.groupby("Expense Report Key")["Expense Report Key"].transform("count")

    car_rental = (
        df.loc[exp_type_norm.eq("car rental")]
        .groupby("Expense Report Key")["Expense Report Key"]
        .transform("count")
        .reindex(df.index, fill_value=0)
    )

    fuel = (
        df.loc[exp_type_norm.str.contains("fuel", na=False)]
        .groupby("Expense Report Key")["Expense Report Key"]
        .transform("count")
        .reindex(df.index, fill_value=0)
    )

    df["_all_car_rental"] = total.eq(car_rental)
    df["_all_fuel"] = total.eq(fuel)

    return df
    
