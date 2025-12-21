from pathlib import Path
from zipfile import ZipFile
import pandas as pd


def load_expense_zips(
    data_folder,
    zip_file="All",
    inner_csv="Project Expenses.csv",
    skiprows=13,
):
    """
    Load and consolidate expense data from one or multiple ZIP files.

    Parameters
    ----------
    data_folder : str or Path
        Folder containing zip files
    zip_file : str
        "All" to process all zip files, else specific zip filename
    inner_csv : str
        CSV filename inside the zip
    skiprows : int
        Number of rows to skip while reading CSV

    Returns
    -------
    pandas.DataFrame
        Consolidated expense data
    """

    data_folder = Path(data_folder)
    data_list = []

    if zip_file == "All":
        zip_paths = data_folder.glob("*.zip")
    else:
        zip_paths = [data_folder / zip_file]

    for zip_path in zip_paths:
        if not zip_path.exists():
            raise FileNotFoundError(f"{zip_path} not found")

        with ZipFile(zip_path) as zf:
            if inner_csv not in zf.namelist():
                raise FileNotFoundError(
                    f"{inner_csv} not found in {zip_path.name}"
                )

            with zf.open(inner_csv) as f:
                df = pd.read_csv(f, skiprows=skiprows)

        # ---- Common cleaning logic ----
        df = df[df["Reimbursement Currency"].notna()]
        df = df[df["Reimbursement Currency"] != "Reimbursement Currency"]

        # Track lineage (auditors love this)
        df["source_zip"] = zip_path.name

        data_list.append(df)

    if not data_list:
        raise ValueError("No data loaded from zip files")

    return pd.concat(data_list, ignore_index=True)
  
import pandas as pd


def normalize_columns(df, column_mapping):
    return df.rename(columns={
        col: column_mapping[col]
        for col in df.columns
        if col in column_mapping
    })


def apply_type_mapping(df, dtype_mapping):
    for col, dtype in dtype_mapping.items():
        if col not in df.columns:
            raise KeyError(f"Missing required column: {col}")

        if dtype.startswith("datetime"):
            df[col] = pd.to_datetime(df[col], errors="coerce")
        else:
            df[col] = df[col].astype(dtype)

    return df
    
import pandas as pd

def load_market_unit_mapping(
    lookup_path: str,
    sheet_name: str = "Market Unit Mapping",
    key_col: int = 0,
    value_col: int = 1,
    lowercase_keys: bool = True
) -> dict:
    """
    Load market unit mapping from Excel and return as dictionary.
    """

    # ---- Validate file path ----
    if not lookup_path:
        raise ValueError("lookup_path cannot be empty")

    try:
        df = pd.read_excel(lookup_path, sheet_name=sheet_name)
    except FileNotFoundError:
        raise FileNotFoundError(f"Excel file not found: {lookup_path}")
    except ValueError as e:
        # Covers invalid sheet name
        raise ValueError(f"Sheet '{sheet_name}' not found in Excel file") from e
    except Exception as e:
        raise RuntimeError("Unexpected error while reading Excel file") from e

    # ---- Validate column indexes ----
    max_index = max(key_col, value_col)
    if df.shape[1] <= max_index:
        raise IndexError(
            f"Excel sheet has only {df.shape[1]} columns, "
            f"but key_col={key_col}, value_col={value_col} were requested"
        )

    # ---- Extract columns ----
    keys = df.iloc[:, key_col]
    values = df.iloc[:, value_col]

    # ---- Validate content ----
    if keys.isna().all():
        raise ValueError("Key column contains only NaN values")

    if values.isna().all():
        raise ValueError("Value column contains only NaN values")

    # ---- Clean keys ----
    keys = keys.astype(str).str.strip()
    if lowercase_keys:
        keys = keys.str.lower()

    # ---- Remove rows with null keys ----
    valid_mask = keys.notna() & (keys != "")
    keys = keys[valid_mask]
    values = values[valid_mask]

    # ---- Handle duplicate keys ----
    if keys.duplicated().any():
        dup_keys = keys[keys.duplicated()].unique().tolist()
        raise ValueError(f"Duplicate keys found in mapping: {dup_keys}")

    return dict(zip(keys, values))
    
LOOKUP_CONFIG = {
    "project_group_type": {
        "sheet": "Project Group Type Mapping",
        "key_col": 0,
        "value_col": 1
    },
    "legal_entity_country": {
        "sheet": "Legal entity Country Mapping",
        "key_col": 0,
        "value_col": 1
    },
    "market_unit": {
        "sheet": "Market Unit Mapping",
        "key_col": 0,
        "value_col": 1
    },
    "private_car_source": {
        "sheet": "Private - Source Mapping",
        "key_col": 0,
        "value_col": 3
    },
    "private_car_type": {
        "sheet": "Private - Source Mapping",
        "key_col": 0,
        "value_col": 4
    },
    "legal_entity": {
        "sheet": "Legal Entity Mapping",
        "key_col": 4,
        "value_col": 7
    },
    "gbl": {
        "sheet": "Legal Entity Mapping",
        "key_col": 4,
        "value_col": 6
    },
    "bu_label": {
        "sheet": "Legal Entity Mapping",
        "key_col": 4,
        "value_col": 5
    },
    "currency_conversion": {
        "sheet": "Currency conversion Mapping",
        "key_col": 0,
        "value_col": 3
    },
    "currency": {
        "sheet": "Currency Mapping",
        "key_col": 0,
        "value_col": 2
    },
    "to_be_uploaded": {
        "sheet": "To be uploaded",
        "key_col": 0,
        "value_col": 3
    }
}
def load_all_lookups(lookup_path: str, lookup_config: dict) -> dict:
    """
    Load all lookup mappings defined in lookup_config.
    Returns a dict of lookup_name -> mapping_dict
    """
    lookups = {}
    errors = {}

    for name, cfg in lookup_config.items():
        try:
            lookups[name] = load_lookup_mapping(
                lookup_path=lookup_path,
                sheet_name=cfg["sheet"],
                key_col=cfg["key_col"],
                value_col=cfg["value_col"]
            )
        except Exception as e:
            errors[name] = str(e)

    if errors:
        raise RuntimeError(
            "Failed to load one or more lookup tables:\n" +
            "\n".join(f"{k}: {v}" for k, v in errors.items())
        )

    return lookups
    lookups = load_all_lookups(lookup_path, LOOKUP_CONFIG)

project_group_type_lookup = lookups["project_group_type"]
legal_entity_country_lookup = lookups["legal_entity_country"]
market_unit_lookup = lookups["market_unit"]
private_car_source_lookup = lookups["private_car_source"]
private_car_type_lookup = lookups["private_car_type"]
legal_entity_lookup = lookups["legal_entity"]
gbl_lookup = lookups["gbl"]
bu_label_lookup = lookups["bu_label"]
currency_conversion_lookup = lookups["currency_conversion"]
currency_mapping_lookup = lookups["currency"]
to_be_uploaded_lookup = lookups["to_be_uploaded"]

from datetime import datetime
from dateutil.relativedelta import relativedelta

def calculate_departure_date(report_extract_date, transaction_date):
    """
    Business rule:
    - If transaction date is older than 2 months from report extract date,
      departure date = first day of (report_extract_date - 2 months)
    - Else departure date = transaction date
    """

    if report_extract_date is None or transaction_date is None:
        return None

    if not isinstance(report_extract_date, datetime) or not isinstance(transaction_date, datetime):
        return None

    month_diff = (
        (report_extract_date.year - transaction_date.year) * 12
        + (report_extract_date.month - transaction_date.month)
    )

    if month_diff > 2:
        edate = report_extract_date - relativedelta(months=2)
        return datetime(edate.year, edate.month, 1)

    return transaction_date

import pandas as pd
from dateutil.relativedelta import relativedelta

# Ensure datetime
data['Report Extract Date'] = pd.to_datetime(data['Report Extract Date'], errors='coerce')
data['Transaction Date'] = pd.to_datetime(data['Transaction Date'], errors='coerce')

# Month difference
month_diff = (
    (data['Report Extract Date'].dt.year - data['Transaction Date'].dt.year) * 12
    + (data['Report Extract Date'].dt.month - data['Transaction Date'].dt.month)
)

# Default departure date
data['Departure Date'] = data['Transaction Date']

# Condition
mask = month_diff > 2

# Calculate capped date
capped_date = (
    data.loc[mask, 'Report Extract Date']
    - pd.DateOffset(months=2)
)

data.loc[mask, 'Departure Date'] = capped_date.dt.to_period('M').dt.to_timestamp()
