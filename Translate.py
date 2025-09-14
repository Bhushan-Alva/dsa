import re
from pathlib import Path
import pandas as pd

def translate_folder(input_folder: str,
                     output_folder: str,
                     translation_file: str,
                     data_sheet: str = "raw_data",
                     translation_sheet: str = "translations") -> None:
    """
    Translate all .xlsb files in `input_folder` using lookups in `translation_file`.
    Output files go to `output_folder` with ' - translated.xlsx' appended.
    Creates a single unmapped.xlsx with two columns:
        UnmappedHeader | UnmappedValue
    """

    input_path = Path(input_folder)
    output_path = Path(output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # ---------- Cleaner ----------
    def clean_text(x):
        if not isinstance(x, str):
            return x
        x = x.replace("\xa0", " ").replace("\n", " ").replace("\r", " ")
        x = re.sub(r"[\x00-\x1F\x7F-\x9F]", "", x)
        x = re.sub(r"\s+", " ", x)
        return x.strip()

    # ---------- Load lookups ----------
    lookup = pd.read_excel(translation_file,
                           sheet_name=translation_sheet,
                           engine="pyxlsb").map(clean_text)

    header_lookup = lookup.iloc[:, [4, 5, 6]].dropna(how="any")
    value_lookup  = lookup.iloc[:, [9, 10]].dropna(how="any")

    header_map = dict(zip(header_lookup.iloc[:, 0], header_lookup.iloc[:, 2]))
    code_map   = {str(k).upper(): v for k, v in
                  zip(header_lookup.iloc[:, 1], header_lookup.iloc[:, 2])}
    value_map  = dict(zip(value_lookup.iloc[:, 0], value_lookup.iloc[:, 1]))

    # regex to capture code inside brackets, e.g. (~WFH1)
    code_pattern = re.compile(r"\(~\s*([^)]+?)\s*\)")

    # to collect all unknowns
    unmapped_headers = set()
    unmapped_values  = set()

    def translate_file(file_path: Path) -> pd.DataFrame:
        df = pd.read_excel(file_path, sheet_name=data_sheet, engine="pyxlsb")
        df.columns = [clean_text(c) for c in df.columns]
        df = df.map(clean_text)

        # ---- header translator ----
        def translate_header(col):
            if col in header_map:
                return header_map[col]
            # extract bracket code e.g. (~WFH1)
            m = code_pattern.search(col)
            if m:
                bracket_code = "~" + m.group(1).upper()
                if bracket_code in code_map:
                    return code_map[bracket_code]
            unmapped_headers.add(col)
            return col  # leave original if not found

        df.columns = [translate_header(c) for c in df.columns]

        # ---- value translator ----
        def translate_cell(x):
            if not isinstance(x, str):
                return x
            parts = [p.strip() for p in x.split(";")]
            out = []
            for p in parts:
                if p in value_map:
                    out.append(value_map[p])
                else:
                    unmapped_values.add(p)
                    out.append(p)
            return "; ".join(out)

        return df.map(translate_cell)

    # ---------- Process every file ----------
    for f in input_path.glob("*.xlsb"):
        print(f"Translating {f.name}")
        translated = translate_file(f)
        out_name = f.stem + " - translated.xlsx"
        translated.to_excel(output_path / out_name, index=False)

    # ---------- Save combined unmapped data ----------
    if unmapped_headers or unmapped_values:
        pd.DataFrame({
            "UnmappedHeader": sorted(unmapped_headers) or [""],
            "UnmappedValue":  sorted(unmapped_values)  or [""]
        }).to_excel(output_path / "unmapped.xlsx", index=False)

    print(f"✅ Completed. Results saved in {output_path.resolve()}")
                       
