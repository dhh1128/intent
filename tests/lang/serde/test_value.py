from intent.lang.serde import Value

PRIMITIVE_VALUES = ["42", "", "hello"]
# In the *_VALUE_PAIRS arrays, it's important that the letter A and the letter b appear
# exactly zero or one times in each value. These letters should also not appear in a
# comment (currently, "#comment"), or in the value of meta (currently, "meta"). This
# lets us generate test cases using string substitution. See test_list_of_value_objs and
# test_dict_of_value_objs for examples.
SUBSTITUTABLE_VALUES = ['A', 'b']
LIST_VALUE_PAIRS = [(['A'], "\n  - A"), (['A', 'b'], "\n  - A\n  - b")]
DICT_VALUE_PAIRS = [({'x': 'A'}, "\n  x: A"), ({'x': 'A', 'y': 'b'}, "\n  x: A\n  y: b")]

def variants(value):
    return [
        Value(value),
        Value(value, comment="#comment"),
        Value(value, comment="  #comment"),
        Value(value, meta="meta"),
        Value(value, meta="meta", comment="#comment"),
        Value(value, meta="meta", comment="  #comment"),
    ]

def str_variants(value):
    return [str(v) for v in variants(value)]

def test_primitive():
    for primitive_val in PRIMITIVE_VALUES:
        serialized_raw = primitive_val
        assert str_variants(serialized_raw) == [ 
            serialized_raw, 
            serialized_raw + "#comment", # primitive values are followed by comments
            serialized_raw + "  #comment", 
            "meta " + serialized_raw, 
            "meta " + serialized_raw + "#comment", 
            "meta " + serialized_raw + "  #comment"
        ]

def test_list():
    for list_val, serialized_raw in LIST_VALUE_PAIRS:
        assert str_variants(list_val) == [
            serialized_raw,
            "#comment" + serialized_raw, # container items are preceded by comments
            "  #comment" + serialized_raw,
            "meta " + serialized_raw,
            "meta #comment" + serialized_raw,
            "meta   #comment" + serialized_raw
        ]

def test_dict():
    for dict_val, serialized_raw in DICT_VALUE_PAIRS:
        assert str_variants(dict_val) == [
            serialized_raw,
            "#comment" + serialized_raw, # container items are preceded by comments
            "  #comment" + serialized_raw,
            "meta " + serialized_raw,
            "meta #comment" + serialized_raw,
            "meta   #comment" + serialized_raw
        ]

def test_list_of_value_objs():
    """
    Prove that Value objects (not primitive values) render correctly as
    list items, no matter whether they're at the beginning or end of a list,
    and now matter what their substructure is.
    """
    # For each variant of each primitive value, represented as a Value object,
    # we're going to permute both list_val and serialized_raw by replacing
    # first "A", then "b", with a each possible variant of a primitive value.
    # This inserts complexly serialized Values directly over the top of primitive
    # ones, in various places. Absolutely nothing else should change.
    #
    # ONLY DEBUG THIS TEST if other tests are passing, because the logic here
    # assumes valid behavior elsewhere.

    def fix_list_val(list_val, variant, to_replace):
        new_list_val = []
        for item in list_val:
            new_list_val.append(variant if item == to_replace else item)
        return new_list_val

    for primitive in PRIMITIVE_VALUES:
        for variant in variants(primitive):
            for to_replace in ['A', 'b']:
                for list_val, serialized_raw in LIST_VALUE_PAIRS:
                    new_list_val = fix_list_val(list_val, variant, to_replace)
                    new_serialized_raw = serialized_raw.replace(to_replace, str(variant))
                    assert str_variants(new_list_val) == [
                        new_serialized_raw,
                        "#comment" + new_serialized_raw,
                        "  #comment" + new_serialized_raw,
                        "meta " + new_serialized_raw,
                        "meta #comment" + new_serialized_raw,
                        "meta   #comment" + new_serialized_raw
                    ]

def test_dict_of_values_objs():
    """
    Prove that Value objects (not primitive values) render correctly as
    list items, no matter whether they're at the beginning or end of a list,
    and now matter what their substructure is.
    """
    # For each variant of each primitive value, represented as a Value object,
    # we're going to permute both list_val and serialized_raw by replacing
    # first "A", then "b", with a each possible variant of a primitive value.
    # This inserts complexly serialized Values directly over the top of primitive
    # ones, in various places. Absolutely nothing else should change.
    #
    # ONLY DEBUG THIS TEST if other tests are passing, because the logic here
    # assumes valid behavior elsewhere.

    def fix_dict_val(dict_val, variant, to_replace):
        new_dict_val = {}
        for key, value in dict_val.items():
            new_dict_val[key] = variant if value == to_replace else value
        return new_dict_val

    for primitive in PRIMITIVE_VALUES:
        for variant in variants(primitive):
            for to_replace in ['A', 'b']:
                for dict_val, serialized_raw in DICT_VALUE_PAIRS:
                    new_list_val = fix_dict_val(dict_val, variant, to_replace)
                    new_serialized_raw = serialized_raw.replace(to_replace, str(variant))
                    assert str_variants(new_list_val) == [
                        new_serialized_raw,
                        "#comment" + new_serialized_raw,
                        "  #comment" + new_serialized_raw,
                        "meta " + new_serialized_raw,
                        "meta #comment" + new_serialized_raw,
                        "meta   #comment" + new_serialized_raw
                    ]

