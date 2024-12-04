import pytest
from intent.lang.serde.commented import *

def test_cc_preconditions():
    with pytest.raises(ValueError, match="mode"):
         CommentedChunk(-25)
    with pytest.raises(ValueError, match="empty"):
         CommentedChunk(LAST_ITEM)
    with pytest.raises(ValueError, match="only above.*LAST_ITEM"):
         CommentedChunk(LIST_VALUE, above="abc")
    with pytest.raises(ValueError, match="DICT_KEY.*:"):
         CommentedChunk(DICT_KEY, chunk="abc", divider="")
    with pytest.raises(ValueError, match="DICT_KEY.*:"):
         CommentedChunk(DICT_KEY, chunk="abc", divider="xyz")
    with pytest.raises(ValueError, match="DICT_KEY.*:"):
         CommentedChunk(DICT_KEY, chunk="x", divider="abc")
    with pytest.raises(ValueError, match="post.*divider"):
         CommentedChunk(LIST_VALUE, chunk="x", post="abc")
    with pytest.raises(ValueError, match="LIST_VALUE.*divider"):
         CommentedChunk(DICT_VALUE, above="something", chunk="x", divider="abc")

def test_cc_values_with_post():
    for above in ["", "#comment above\n"]:
        for pre in ["", "  "]:
            for space_after in ["", " ", "    "]:
                for mode in [LIST_VALUE, DICT_VALUE]:
                    line = pre + "a" + space_after + "#b"
                    # Above can't appear on DICT_VALUE, but so in those iterations, suppress it.
                    if mode == DICT_VALUE: above = ""
                    cv = CommentedChunk.from_line(mode, line=line, above=above)
                    assert cv.mode == mode
                    assert cv.pre == pre
                    assert cv.chunk == "a"
                    assert cv.divider == space_after
                    assert cv.post == "#b"
                    assert cv.above == above
                    assert str(cv) == "a"
                    assert cv.text == above + line

def test_cc_values_without_post():
    for above in ["", "#comment above\n"]:
        for pre in ["", "  "]:
            for space_after in ["", " ", "    "]:
                for mode in [LIST_VALUE, DICT_VALUE]:
                    line = pre + "a" + space_after
                    # Above can't appear on DICT_VALUE, but so in those iterations, suppress it.
                    if mode == DICT_VALUE: above = ""
                    cv = CommentedChunk.from_line(mode, line=line, above=above)
                    assert cv.mode == mode
                    assert cv.pre == pre
                    assert cv.chunk == "a"
                    assert cv.divider == space_after
                    assert cv.post == ""
                    assert cv.above == above
                    assert str(cv) == "a"
                    assert cv.text == above + line

def test_cc_dictkey():
    for above in ["", "#comment above\n"]:
        for pre in ["", "  "]:
            for space_after in ["", " ", "    "]:
                line = pre + "a" + space_after + ": " # add extra space to make sure it's not included in the chunk
                cv = CommentedChunk.from_line(DICT_KEY, line=line, above=above)
                assert cv.mode == DICT_KEY
                assert cv.above == above
                assert cv.pre == pre
                assert cv.chunk == "a"
                assert cv.divider == space_after + ":"
                assert cv.post == ""
                assert cv.above == above
                assert str(cv) == "a"
                assert cv.text == above + line[:-1] # space after colon isn't considered part of the chunk

def test_cc_last_item():
    for above in ["abc", "#comment above\n", "#comment above\n  # comment above\n  "]:
        cv = CommentedChunk(LAST_ITEM, above=above)
        assert cv.mode == LAST_ITEM
        assert cv.pre == ""
        assert cv.chunk == ""
        assert cv.divider == ""
        assert cv.post == ""
        assert cv.above == above
        assert str(cv) == ""
        assert cv.text == above
"""
def test_commented_value_head_and_tail():
    cv = CommentedChunk.from_line("a #b", above="#comment\n#comment")
    assert str(cv) == "a"
    assert cv.chunk == "a"
    assert cv.text == "#comment\n#comment\na #b"
    assert cv.post == "#b"
    assert cv.above == "#comment\n#comment"
    cv = CommentedChunk("a", above="#comment\n#comment", post="#b")
    assert str(cv) == "a"
    assert cv.chunk == "a"
    assert cv.text == "#comment\n#comment\na #b"
    assert cv.post == "#b"
    assert cv.above == "#comment\n#comment"

def test_commented_value_tail_big_divider():
    cv = CommentedChunk.from_line("a    #b")
    assert str(cv) == "a"
    assert cv.text == "a    #b"
    assert cv.chunk == "a"
    assert cv.post == "#b"

LIST_WITH_MID_COMMENT = ["a", "#b", "c"]
LIST_STARTS_WITH_COMMENT = sorted(LIST_WITH_MID_COMMENT)
LIST_ENDS_WITH_COMMENT = sorted(LIST_WITH_MID_COMMENT, reverse=True)
INDENTED_LIST = ['  ' + item for item in LIST_WITH_MID_COMMENT]
CL_VARIANTS = [LIST_WITH_MID_COMMENT, LIST_STARTS_WITH_COMMENT, LIST_ENDS_WITH_COMMENT, INDENTED_LIST]

def test_commented_list_simple():
    for l in CL_VARIANTS:
        cl = CommentedList(l)
        assert str(cl) == str(l)

def test_commented_list_with_commented_values():
    l = [CommentedChunk.from_line("a #comment"), "#b", "c", CommentedChunk.from_line("d #comment")]
    cl = CommentedList(l)
    assert str(cl) == str(l)


"""