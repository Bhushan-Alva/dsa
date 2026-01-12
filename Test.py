def rental_car_usage(
    expense_type: str,
    expense_key: str,
    emp_country: str,
    cot: str,
    approved_amount: float,
    all_car_rental: bool,
    all_fuel: bool,
    **lookups,
) -> float:

    if emp_country == "GB":
        return 0.0

    fuel_price = lookups["rental_fuel_price_mapping"].get(
        cot, lookups["oc_mapping"]
    )

    split = lookups["rental_country_split_mapping"].get(
        emp_country, lookups["oc_mapping"]
    )

    expense_type_norm = expense_type.strip().casefold()

    # CONDITION 1 — all rows car rental
    if all_car_rental:
        return (approved_amount * split) / fuel_price

    # CONDITION 2 — all rows fuel
    if all_fuel:
        return approved_amount / fuel_price

    # CONDITION 3 — rental but not fuel
    if "rental" in expense_type_norm and "fuel" not in expense_type_norm:
        return approved_amount / fuel_price

    # CONDITION 4 — not fuel
    if "fuel" not in expense_type_norm:
        return 0.0

    return approved_amount / fuel_price
    
