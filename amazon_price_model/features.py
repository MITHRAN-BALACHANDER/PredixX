# features.py

import re
import numpy as np

def extract_numeric_specs(text: str) -> dict:
    if not isinstance(text, str):
        return {}

    t = text.lower()

    out = {}

    # pack of X
    m = re.search(r"pack(?:\s*of)?\s*(\d+)", t)
    out["pack_qty"] = float(m.group(1)) if m else np.nan

    # Value: X  (your dataset shows "Value: 72.0")
    m = re.search(r"value:\s*([\d.]+)", t)
    out["value_num"] = float(m.group(1)) if m else np.nan

    # Unit: (Fl Oz) or oz
    m = re.search(r"unit:\s*([a-zA-Z ]+)", t)
    # out["unit_str"] = m.group(1).strip() if m else None

    # fluid ounce typical pattern
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:fl oz|fluid ounce)", t)
    out["fl_oz"] = float(m.group(1)) if m else np.nan

    # ounces
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:oz|ounce)", t)
    out["oz"] = float(m.group(1)) if m else np.nan

    # milliliters
    m = re.search(r"(\d+(?:\.\d+)?)\s*ml", t)
    out["ml"] = float(m.group(1)) if m else np.nan

    # grams
    m = re.search(r"(\d+(?:\.\d+)?)\s*g\b", t)
    out["grams"] = float(m.group(1)) if m else np.nan

    # pounds (lb / lbs)
    m = re.search(r"(\d+(?:\.\d+)?)\s*(?:lb|lbs|pound)", t)
    out["pounds"] = float(m.group(1)) if m else np.nan

    return out
