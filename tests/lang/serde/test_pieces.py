import pytest
from intent.lang.serde.pieces import *

def test_chunk_preconditions():
    with pytest.raises(ValueError, match="mode"):
         Chunk(-25)
    with pytest.raises(ValueError, match="only above.*TAIL"):
         Chunk(Chunk.Mode.LIST_VALUE, above="abc")
    with pytest.raises(ValueError, match="DICT_KEY.*:"):
         Chunk(Chunk.Mode.DICT_KEY, chunk="abc", divider="")
    with pytest.raises(ValueError, match="DICT_KEY.*:"):
         Chunk(Chunk.Mode.DICT_KEY, chunk="abc", divider="xyz")
    with pytest.raises(ValueError, match="DICT_KEY.*:"):
         Chunk(Chunk.Mode.DICT_KEY, chunk="x", divider="abc")
    with pytest.raises(ValueError, match="post.*divider"):
         Chunk(Chunk.Mode.LIST_VALUE, chunk="x", post="abc")
    with pytest.raises(ValueError, match="LIST_VALUE.*divider"):
         Chunk(Chunk.Mode.DICT_VALUE, above="something", chunk="x", divider="abc")

def test_empty_chunk():
    assert Chunk(Chunk.Mode.TAIL).is_empty
    assert not Chunk(Chunk.Mode.TAIL, above="abc").is_empty


def adjust_expected_for_quotes(pre, chunk, divider):
    e_pre = pre
    e_divider = divider
    if chunk[0] in '\'"':
        e_pre = pre + chunk[0]
        e_divider = chunk[0] + divider
        chunk = chunk[1:-1]
    return e_pre, chunk, e_divider

def value_ctor_for_mode(mode: Chunk.Mode):
    """Return the constructor for the given mode."""
    if mode == Chunk.Mode.LIST_VALUE:
        return Chunk.from_listvalue
    if mode == Chunk.Mode.DICT_VALUE:
        # We'll be calling from_dictvalue() and from_listvalue()
        # interchangeable, but they have slightly different signatures
        # because from_dictvalue() doesn't allow above to be passed.
        # Write an adapter that ignore the above parameter.
        return lambda line, above: Chunk.from_dictvalue(line)
    
def test_chunk_values_with_post():
    # Try parsing with and without comments above
    for above in ["", "#comment above\n"]:
        # Try it with and without an indent
        for pre in ["", "  "]:
            # Try it with varying amounts of whitespace after chunk 
            for divider in ["", " ", "    "]:
                # Try it in multiple modes
                for mode in [Chunk.Mode.LIST_VALUE, Chunk.Mode.DICT_VALUE]:
                    # DICT_VALUE can't have an above, so collapse that permutation.
                    if mode == Chunk.Mode.DICT_VALUE: above = ""
                    # Try it with and without quotes around the chunk
                    for chunk in ['a', '"a"', "'a'"]:
                        # Build the corresponding line that needs parsing.
                        line = pre + chunk + divider + "#b"
                        # Decide what's expected based on whether quotes are used or not.
                        expected_pre, chunk, expected_divider = adjust_expected_for_quotes(pre, chunk, divider)
                        ctor = value_ctor_for_mode(mode)
                        cv = ctor(line=line, above=above)
                        assert cv.mode == mode
                        assert cv.pre == expected_pre
                        assert cv.interpreted_chunk == "a"
                        assert cv.chunk == chunk
                        assert cv.divider == expected_divider
                        assert cv.post == "#b"
                        assert cv.above == above
                        assert str(cv) == "a"
                        assert cv.code == above + line

def test_chunk_values_without_post():
    # Try parsing with and without comments above
    for above in ["", "#comment above\n"]:
        # Try it with and without an indent
        for pre in ["", "  "]:
            # Try it with varying amounts of whitespace after chunk 
            for divider in ["", " ", "    "]:
                # Try it in multiple modes
                for mode in [Chunk.Mode.LIST_VALUE, Chunk.Mode.DICT_VALUE]:
                    # DICT_VALUE can't have an above, so collapse that permutation.
                    if mode == Chunk.Mode.DICT_VALUE: above = ""
                    # Try it with and without quotes around the chunk
                    for chunk in ['a', '"a"', "'a'"]:
                        # Build the corresponding line that needs parsing.
                        line = pre + chunk + divider
                        # Decide what's expected based on whether quotes are used or not.
                        expected_pre, chunk, expected_divider = adjust_expected_for_quotes(pre, chunk, divider)
                        ctor = value_ctor_for_mode(mode)
                        cv = ctor(line=line, above=above)
                        assert cv.mode == mode
                        assert cv.pre == expected_pre
                        assert cv.interpreted_chunk == "a"
                        assert cv.chunk == chunk
                        assert cv.divider == expected_divider
                        assert cv.post == ""
                        assert cv.above == above
                        assert str(cv) == "a"
                        assert cv.code == above + line

def test_chunk_dictkey():
    # Try parsing with and without comments above
    for above in ["", "#comment above\n"]:
        # Try it with and without an indent
        for pre in ["", "  "]:
            # Try it with varying amounts of whitespace after chunk 
            for divider in ["", " ", "    "]:
                # Try it with and without quotes around the chunk
                for chunk in ['a', '"a"', "'a'"]:
                    line = pre + chunk + divider + ": " # add extra space to make sure it's not included in the chunk
                    # Decide what's expected based on whether quotes are used or not.
                    expected_pre, chunk, expected_divider = adjust_expected_for_quotes(pre, chunk, divider)
                    cv = Chunk.from_dictkey(line=line, above=above)
                    assert cv.mode == Chunk.Mode.DICT_KEY
                    assert cv.above == above
                    assert cv.pre == expected_pre
                    assert cv.interpreted_chunk == "a"
                    assert cv.chunk == chunk
                    assert cv.divider == expected_divider + ":"
                    assert cv.post == ""
                    assert cv.above == above
                    assert str(cv) == "a"
                    assert cv.code == above + line[:-1] # space after colon isn't considered part of the chunk

def test_chunk_dictkey_with_no_value():
    Chunk.from_dictkey("a:") # this used to throw an exception

def test_chunk_tail():
    for above in ["abc", "#comment above\n", "#comment above\n  # comment above\n  "]:
        cv = Chunk.from_tail(above=above)
        assert cv.mode == Chunk.Mode.TAIL
        assert cv.pre == ""
        assert cv.chunk == ""
        assert cv.divider == ""
        assert cv.post == ""
        assert cv.above == above
        assert str(cv) == ""
        assert cv.code == above

LIST_WITH_MID_COMMENT = [Chunk.from_listvalue(item) for item in ["a", "'def' #comment", "#pure comment", "content", "  indented content"]]
LIST_STARTS_WITH_COMMENT = sorted(LIST_WITH_MID_COMMENT)
LIST_ENDS_WITH_COMMENT = sorted(LIST_WITH_MID_COMMENT, reverse=True)

def assert_order(list, *items):
    for i, item in enumerate(items):
        assert list[i].code == item

def test_cl_sort():
    assert_order(LIST_STARTS_WITH_COMMENT, "#pure comment", "a", "content", "'def' #comment", "  indented content")
    assert_order(LIST_ENDS_WITH_COMMENT, "  indented content", "'def' #comment", "content", "a", "#pure comment")

INDENTED_LIST = [Chunk.from_listvalue('  ' + item.code) for item in LIST_WITH_MID_COMMENT]
CL_VARIANTS = [LIST_WITH_MID_COMMENT, LIST_STARTS_WITH_COMMENT, LIST_ENDS_WITH_COMMENT, INDENTED_LIST]

def test_commented_list_as_str():
    assert str(LIST_WITH_MID_COMMENT) == '[a, def, , content, indented content]'

def test_commented_list_as_text():
    assert List(LIST_WITH_MID_COMMENT).code == "a\n'def' #comment\n#pure comment\ncontent\n  indented content\n"