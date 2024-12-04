from intent.lang.serde.commented import CommentedList, CommentedValue

def test_commented_value_tail():
    cv = CommentedValue.from_line("a #b")
    assert str(cv) == "a"
    assert cv.value == "a"
    assert cv.text == "a #b"
    assert cv.tail == "#b"
    cv = CommentedValue("a", tail="#b")
    assert str(cv) == "a"
    assert cv.value == "a"
    assert cv.text == "a #b"
    assert cv.tail == "#b"

def test_commented_value_head_and_tail():
    cv = CommentedValue.from_line("a #b", head="#comment\n#comment")
    assert str(cv) == "a"
    assert cv.value == "a"
    assert cv.text == "#comment\n#comment\na #b"
    assert cv.tail == "#b"
    assert cv.head == "#comment\n#comment"
    cv = CommentedValue("a", head="#comment\n#comment", tail="#b")
    assert str(cv) == "a"
    assert cv.value == "a"
    assert cv.text == "#comment\n#comment\na #b"
    assert cv.tail == "#b"
    assert cv.head == "#comment\n#comment"

def test_commented_value_tail_big_divider():
    cv = CommentedValue.from_line("a    #b")
    assert str(cv) == "a"
    assert cv.text == "a    #b"
    assert cv.value == "a"
    assert cv.tail == "#b"

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
    l = [CommentedValue.from_line("a #comment"), "#b", "c", CommentedValue.from_line("d #comment")]
    cl = CommentedList(l)
    assert str(cl) == str(l)


