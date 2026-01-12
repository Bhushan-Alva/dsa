def rental_car_usage(
    expense_type: str,
    expense_key: str,
    emp_country: str,
    cot: str,
    approved_amount: float,
    *,
    rental_country_split_mapping: dict,
    rental_fuel_price_mapping: dict,
    oc_mapping: float
) -> float:
    if emp_country == "GB":
        return 0.0

    expense_type_norm = expense_type.strip().casefold()

    if "car rental" in expense_type_norm:
        split = rental_country_split_mapping.get(emp_country, oc_mapping)
        fuel_price = rental_fuel_price_mapping.get(cot, oc_mapping)
        return (approved_amount * split) / fuel_price

    if "fuel" in expense_type_norm:
        fuel_price = rental_fuel_price_mapping.get(cot, oc_mapping)
        return approved_amount / fuel_price

    if "rental" in expense_type_norm and "fuel" not in expense_type_norm:
        fuel_price = rental_fuel_price_mapping.get(cot, oc_mapping)
        return approved_amount / fuel_price

    return approved_amount / rental_fuel_price_mapping.get(cot, oc_mapping)
    
