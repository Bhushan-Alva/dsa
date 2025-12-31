def lpt_usage(emp_country, country_of_transaction, cost, **lookups):
    if not cost:
        return 0.0

    if country_of_transaction:
        rate_lookup = lookups.get("lpt_country_mapping", {})
        rate_key = rate_lookup.get(country_of_transaction.lower(), "")
        rate = _safe_rate(lookups.get("transaction_country_rail_rate", {}), rate_key)

    else:
        if emp_country == "FR":
            rate = _safe_rate(lookups.get("emp_country_rail_rate", {}), emp_country.lower())
        else:
            rate = _safe_rate(lookups.get("emp_country_bus_rate", {}), emp_country.lower())

    return cost / rate if rate else 0.0
    
