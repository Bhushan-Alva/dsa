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
  
