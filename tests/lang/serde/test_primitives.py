import pytest
import random

from intent.lang.serde.primitives import *

def test_bool():
    for value in ["true", "on", "yes", "True", "On", "Yes", "TRUE", "ON", "YES"]:
        assert is_bool(value)
        assert deserialize_bool(value) == True
    for value in ["tRUE", "oN", "yES"]:
        assert not is_bool(value)
        with pytest.raises(ValueError):
            deserialize_bool(value)
    for value in ["false", "off", "no", "False", "Off", "No", "FALSE", "OFF", "NO"]:
        assert is_bool(value)
        assert deserialize_bool(value) == False
    for value in ["fALSE", "oFF", "nO"]:
        assert not is_bool(value)
        with pytest.raises(ValueError):
            deserialize_bool(value)

def test_null():
    for value in ["null", "Null", "NULL", "~"]:
        assert is_null(value)
        assert deserialize_null(value) == None
    for value in ["nULL", "none", "nil"]:
        assert not is_null(value)
        with pytest.raises(ValueError):
            deserialize_null(value)

def test_int():
    prefixes = ["0x", "", "0o", "0b"]
    for sign in ["", "+", "-"]:
        for value, prefix_count in [("0", 4), ("1", 4), ("1011", 4), ("7234623", 3), ("293857", 2), ("ab283590028", 1)]:
            for i, prefix in enumerate(prefixes):
                variants = [value]
                if i < prefix_count:
                    if len(value) > 1:
                        random_index = random.randint(1, len(value) - 1)
                        variants.append(value[:random_index] + '_' + value[random_index:])
                    for variant in variants:
                        txt = prefix + variant
                        assert is_int(txt)
                        assert deserialize_int(txt) == eval(txt.replace("_", ""))

def test_float():
    for value in ["3.14159", "3.14159e301", ".nan", "-.inf", '+.inf', '.inf', '0.0', '0.', '.0', '0e0', '0e+0', '0e-0', '0.0e0', '0.0e+0', '0.0e-0']:
        assert is_float(value)
        if value == ".nan":
            # NaN is not equal to itself
            assert deserialize_float(value) != float('nan')
        elif '.inf' in value:
            assert deserialize_float(value) == float(value.replace('.', ''))
        else:
            assert deserialize_float(value) == float(value)
    for value in [".infinity", "3.1g7", "3.1e500"]:
        assert not is_float(value)
        with pytest.raises(ValueError):
            deserialize_float(value)

