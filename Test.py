def get_travel_category(country_of_transaction, legal_entity, entity_country_lookup):
    """
    Pure Python travel category logic.

    Rules:
    - If country_of_transaction is blank / None / missing → "Unknown"
    - Else if legal entity country matches transaction country → "Local"
    - Else → "Abroad"
    """

    # ---- First check: missing / blank country ----
    if country_of_transaction is None:
        return "Unknown"

    country = str(country_of_transaction).strip()
    if not country:
        return "Unknown"

    # ---- Lookup legal entity country ----
    if legal_entity is None:
        return "Abroad"   # business choice: no entity match

    entity_key = str(legal_entity).strip().lower()
    entity_country = entity_country_lookup.get(entity_key)

    if not entity_country:
        return "Abroad"

    # ---- Final comparison ----
    if entity_country.strip().lower() == country.lower():
        return "Local"

    return "Abroad"
    
