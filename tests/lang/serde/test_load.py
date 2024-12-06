import pytest
from intent.lang.serde import load

def test_load_simple():
    x = load("a: b\nc: d")
    assert x == {"a": "b", "c": "d"}

def test_load_empty():
    x = load("")
    assert x == {}

def test_load_one_indent():
    x = load("a:\n  c: d")
    assert x == {"a": {"c": "d"}}

def test_premature_indent():
    with pytest.raises(ValueError):
        x = load("  a:\n  c: d")

def test_too_deep_indent():
    with pytest.raises(ValueError):
        x = load("a:\n    c: d")

def test_load_three_indent():
    with pytest.raises(ValueError):
        x = load("a:\n   c: d")

def test_load_list_one_item():
    x = load("a:\n  - d")
    assert x == {"a": ["d"]}

def test_load_list_multiple_items():
    x = load("a:\n  - d\n  - e")
    assert x == {"a": ["d", "e"]}

def test_load_list_then_other_key_value_pair():
    x = load("a:\n  - d\n  - e\nb: c")
    assert x == {"a": ["d", "e"], "b": "c"}

def test_load_list_nested_no_space():
    x = load("a:\n  -\n    - e")
    assert x == {"a": [["e"]]}

