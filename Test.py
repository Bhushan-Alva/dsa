import pandas as pd

def build_console_key(row, source, key_map, sep="|"):
    """
    Build a composite console key based on source-specific columns

    row: Pandas Series (df row)
    source: string (e.g. "Taxi", "Hotel")
    key_map: your keys dictionary
    sep: separator for key parts
    """

    columns = key_map.get(source, [])

    values = []
    for col in columns:
        val = row.get(col, "")
        
        if pd.isna(val):
            val = ""
        else:
            val = str(val).strip()

        values.append(val)

    return sep.join(values)
    
