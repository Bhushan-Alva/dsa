def is_blank(x):
    if x is None:
        return True
    if isinstance(x, float):  # NaN
        return True
    if isinstance(x, str) and x.strip() == "":
        return True
    return False


def calculate_usage(emp_country, country_of_transaction, cost, lookups):

    if not cost:
        return 0.0

    # ===== Excel: IF(BK2="") =====
    if is_blank(country_of_transaction):

        # Excel: IF(P2="FR")
        if emp_country == "FR":
            rate = safe_rate(
                lookups["country_bus_rate"],
                emp_country
            )
        else:
            rate = safe_rate(
                lookups["country_bus_rate_non_fr"],
                emp_country
            )

    else:
        mapped_country = lookups["ipt_country_mapping"].get(
            safe_lower(country_of_transaction),
            ""
        )

        if emp_country == "FR":
            rate = safe_rate(
                lookups["emp_country_call_rate"],
                mapped_country
            )
        else:
            rate = safe_rate(
                lookups["emp_country_bus_rate"],
                mapped_country
            )

    return cost / rate if rate else 0.0
    
