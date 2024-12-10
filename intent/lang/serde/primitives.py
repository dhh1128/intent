import math
import re

BOOL_PAT = re.compile(r"^([tT]rue|[fF]alse|[oO]n|[oO]ff|[yY]es|[nN]o|TRUE|FALSE|ON|OFF|YES|NO)$")

def is_bool(txt) -> bool:
    return BOOL_PAT.match(txt) is not None

def deserialize_bool(txt) -> bool:
    m = BOOL_PAT.match(txt)
    if not m: raise ValueError(f"Invalid boolean value: {txt}")
    word = m.group(1).lower()
    return True if word[0] in "ty" or word[-1] == 'n' else False

def serialize_bool(value: bool) -> str:
    return "true" if value else "false"

NULL_PAT = re.compile(r"^([nN]ull|NULL|~)$")

def is_null(txt) -> bool:
    return NULL_PAT.match(txt) is not None

def deserialize_null(txt):
    m = NULL_PAT.match(txt)
    if not m: raise ValueError(f"Invalid null value: {txt}")
    return None

def serialize_null(_=None) -> str:
    return "null"

DEC_INT_PAT = re.compile(r"^([-+]?)[0-9](_?[0-9]+)*$")
HEX_INT_PAT = re.compile(r"^([-+]?)0x[0-9a-fA-F](_?[0-9a-fA-F]+)*$")
BIN_INT_PAT = re.compile(r"^([-+]?)0b[01](_?[01]+)*$")
OCT_INT_PAT = re.compile(r"^([-+]?)0o[0-9](_?[0-7]+)*$")

def is_int(txt) -> bool:
    if DEC_INT_PAT.match(txt): return True
    if HEX_INT_PAT.match(txt): return True
    if BIN_INT_PAT.match(txt): return True
    if OCT_INT_PAT.match(txt): return True
    return False

def deserialize_int(txt: str):
    m = DEC_INT_PAT.match(txt)
    if m: return int(txt.replace("_", ""))
    m = HEX_INT_PAT.match(txt)
    if m: return int(txt[2:].replace("_", ""), 16)
    m = BIN_INT_PAT.match(txt)
    if m: return int(txt[2:].replace("_", ""), 2)
    m = OCT_INT_PAT.match(txt)
    if m: return int(txt[2:].replace("_", ""), 8)
    raise ValueError(f"Invalid int value: {txt}")

def serialize_int(n, base: int=10) -> str:
    if base == 10: return str(n)
    if base == 16: return f"0x{n:x}"
    if base == 2: return f"0b{n:b}"
    if base == 8: return f"0o{n:o}"
    raise ValueError(f"Invalid base: {base}")

FLOATING_POINT_PAT = re.compile('^([-+]?(?:[0-9]*\.[0-9]+|[0-9]+\.?)(?:[eE][-+]?([0-9]+))?|[-+]?\.inf|\.nan)$')

def is_float(txt) -> bool:
    m = FLOATING_POINT_PAT.match(txt)
    if m: 
        return True if m.group(2) is None or int(m.group(2)) <= 308 else False
    return False

def deserialize_float(txt: str):
    m = FLOATING_POINT_PAT.match(txt)
    if not m: raise ValueError(f"Invalid float value: {txt}")
    if '.inf' in txt:
        return float('inf') if txt[0] != '-' else float('-inf')
    elif '.nan' in txt:
        return float('nan')
    else:
        exponent = m.group(2)
        if exponent:
            if int(exponent) <= 308:
                return float(txt)
            else:
                raise ValueError(f"Float value overflows: {txt}")
        else:
            return float(txt)

def serialize_float(n, base: int=10) -> str:
    if math.isinf(n): 
        return "-.inf" if n < 0 else ".inf"
    elif math.nan(n):
        return ".nan"
    else:
        return str(n)


