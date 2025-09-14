import re
from pathlib import Path
import pandas as pd

def translate_folder(input_folder: str,
                     output_folder: str,
                     translation_file: str,
                     data_sheet: str = "raw_data",
                     translation_sheet: str = "translations") -> None:
    """
    Translate every .xlsb file in `input_folder` using lookups
    from `translation_file` and save results to `output_folder`.

    Each output file name is "<original name> - translated.xlsx".
    An unmapped_values.xlsx is also created listing all unknown values.

    Parameters
    ----------
    input_folder : str
        Folder path containing the data files to translate (.xlsb).
    output_folder : str
        Folder path where translated files will be saved.
    translation_file : str
        Path to the workbook that holds the 'translations' sheet.
    data_sheet : str, default 'raw_data'
        Name of the sheet in each input file that needs translation.
    translation_sheet : str, default 'translations'
        Name of the sheet that holds header & value lookups.
    """

    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # ---------- Cleaning helper ----------
    def clean_text(x):
        if not isinstance(x, str):
            return x
        x = x.replace("\xa0", " ").replace("\n", " ").replace("\r", " ")
        x = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", x)
        x = re.sub(r"\s+", " ", x)
        return x.strip()

    # ---------- Load and clean lookup ----------
    lookup = pd.read_excel(translation_file,
                           sheet_name=translation_sheet,
                           engine="pyxlsb").map(clean_text)

    header_lookup = lookup.iloc[:, [4, 5, 6]].dropna(how="any")
    value_lookup  = lookup.iloc[:, [9, 10]].dropna(how="any")

    header_map = dict(zip(header_lookup.iloc[:, 0], header_lookup.iloc[:, 2]))
    code_map   = dict(zip(header_lookup.iloc[:, 1], header_lookup.iloc[:, 2]))
    value_map  = dict(zip(value_lookup.iloc[:, 0],  value_lookup.iloc[:, 1]))

    # ---------- Per-file translator ----------
    def translate_file(file_path: Path, missing_set: set) -> pd.DataFrame:
        # read and clean
        df = pd.read_excel(file_path, sheet_name=data_sheet, engine="pyxlsb")
        df.columns = [clean_text(c) for c in df.columns]
        df = df.map(clean_text)

        # header translation
        def translate_header(col):
            if col in header_map:
                return header_map[col]
            for code, eng in code_map.items():
                if col.endswith(code[-5:]):
                    return eng
            return col
        df.columns = [translate_header(c) for c in df.columns]

        # value translation with multi-choice & missing log
        def translate_cell(x):
            if not isinstance(x, str):
                return x
            parts = [p.strip() for p in x.split(";")]
            out = []
            for p in parts:
                if p in value_map:
                    out.append(value_map[p])
                else:
                    missing_set.add(p)
                    out.append(p)
            return "; ".join(out)

        return df.map(translate_cell)

    # ---------- Process all files ----------
    missing_values = set()

    for f in input_path.glob("*.xlsb"):
        print(f"Translating: {f.name}")
        translated_df = translate_file(f, missing_values)
        out_name = f.stem + " - translated.xlsx"
        translated_df.to_excel(output_path / out_name, index=False)

    # ---------- Save all unmapped values ----------
    if missing_values:
        pd.DataFrame(sorted(missing_values), columns=["UnmappedValue"])\
            .to_excel(output_path / "unmapped_values.xlsx", index=False)

    print(f"✅ Completed. Output saved in: {output_path.resolve()}")
