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

def test_load_list():
    x = load("a:\n  - d")
    assert x == {"a": ["d"]}

