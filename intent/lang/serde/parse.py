from abc import ABC, abstractmethod
from enum import Enum
from typing import Tuple

from .code import Code
from .commented import CommentedDict, CommentedList, CommentedChunk, CCMode, Expansion

__all__ = ["load", "dump", "Value"]

def end_of_indent(data: str, i: int, end: int) -> tuple:
    while i < end:
        c = data[i]
        if c != ' ': break
        i += 1
    return i

def raise_on_bad_indent(data: str, start_of_line: int, end_of_indent: int, line_num: int, current_indent: int, allow_nest: bool = True) -> tuple:
    if data[end_of_indent] == '\t':
        raise ValueError(f"Invalid indent (tab) on line {line_num}. Only 2-space indents are allowed.")
    indent = end_of_indent - start_of_line
    if indent % 2 == 1:
        raise ValueError(f"Bad indent ({indent} spaces) on line {line_num}. Only 2-space indents are allowed.")
    if indent > current_indent + 2:
        raise ValueError(f"Too indented ({indent} spaces) on line {line_num}. Expected max {current_indent + 2}.")

def end_of_line(data: str, i: int, end: int) -> int:
    while i < end:
        c = data[i]
        if c in '\n\r': return i
        i += 1
    return end

def skip_eol(data: str, i: int, end: int) -> int:
    if i < end and data[i] == '\r': i += 1
    if i < end and data[i] == '\n': i += 1
    return i

def split_line(data: str, i: int, eof: int) -> Tuple[int, int, str]:
    eoi = end_of_indent(data, i, eof)
    eol = end_of_line(data, i)
    line = data[i:eol]
    return eoi, eol, line

class ParsePoint:
    def __init__(self, data: str, offset: int = 0, line_num: int = 1, indent = 0, above=''):
        self.data = data
        self.start = offset
        self.line_num = line_num
        self.indent = indent
        self.above = above

class Parser(ABC):
    parent: 'Parser'

    def __init__(self, parent: 'Parser' = None):
        self.parent = parent

    @abstractmethod
    def parse(self, start_at: ParsePoint) -> Tuple[Code, ParsePoint]:
        pass

class UnknownContainerParser(Parser):
    def parse(self, start_at: ParsePoint) -> Tuple[Code, ParsePoint]:
        """
        Starts parsing what's inside a container without knowing what kind of container
        it is, and consumes just enough text to figure out whether to pass the job off
        to a DictParser or a ListParser.
        """
        above = start_at.above
        start_of_line = start_at.offset
        line_num = start_at.line_num
        data = start_at.data
        eof = len(data)

        while start_of_line < eof:
            end_of_indent, end_of_line, line = split_line(data, start_of_line, eof)
            raise_on_bad_indent(data, start_of_line, end_of_indent, line_num, start_at.indent, allow_nest=False)
            if end_of_indent == end_of_line:
                above += line + '\n'
            else:
                first_char = data[end_of_indent]
                if first_char == '#':
                    above += line
                else:
                    this_indent = end_of_indent - start_of_line
                    if this_indent > start_at.indent:
                        raise ValueError(f"Premature indent on line {line_num}.")
                    elif this_indent < start_at.indent:
                        # We found something other than a comment that is less indented than us,
                        # so we're done parsing.
                        code = CommentedChunk(CCMode.LAST_ITEM, above)
                        resume_at = ParsePoint(data, start_of_line, line_num, start_at.indent, above)
                        return code, resume_at
                    else:
                        continue_at = ParsePoint(data, start_of_line, line_num, start_at.indent, above)
                        if first_char == '-':
                            handoff_to = ListParser(self)
                        else:
                            handoff_to = DictParser(self)
                        code, resume_at = handoff_to.parse(continue_at)
                        return code, resume_at
            start_of_line = skip_eol(data, end_of_line, eof)
            line_num += 1

class DictParser(Parser):
    def parse(self, start_at: ParsePoint) -> Tuple[CommentedDict, ParsePoint]:
        """
        Implements a state machine to parse a dictionary from a string. For docs on the state
        machine, see https://bit.ly/3OE2UJo.
        """
        above = start_at.above
        start_of_line = start_at.offset
        line_num = start_at.line_num
        data = start_at.data
        eof = len(data)
        result: CommentedDict = CommentedDict()
        prev_key: CommentedChunk = None
        prev_value: CommentedChunk = None

        while start_of_line < eof:
            end_of_indent, end_of_line, line = split_line(data, start_of_line, eof)
            raise_on_bad_indent(data, start_of_line, end_of_indent, line_num, start_at.indent, allow_nest=False)
            if end_of_indent == end_of_line:
                above += line + '\n'
            else:
                first_char = data[end_of_indent]
                if first_char == '#':
                    above += line
                elif first_char == '-':
                    raise ValueError(f"Expected key: value instead of list item on line {line_num}.")
                else:
                    this_indent = end_of_indent - start_of_line
                    if this_indent == start_at.indent + 2:
                        if prev_value is None:
                            raise ValueError(f"Premature indent on line {line_num}. Expected key: value.")
                        continue_at = ParsePoint(data, start_of_line, line_num, this_indent, above)
                        above = ''
                        handoff_to = UnknownContainerParser(self)
                        details, resume_at = handoff_to.parse(continue_at)
                        expansion = Expansion(prev_value, details)
                        result[prev_key] = expansion
                    elif this_indent > start_at.indent:
                        assert not "In theory, this should have been caught in raise_on_bad_intent"
                    elif this_indent < start_at.indent:
                        if above:
                            result[None] = CommentedChunk(CCMode.LAST_ITEM, above)
                        resume_at = ParsePoint(data, start_of_line, line_num, this_indent)
                        return result, resume_at
                    else:
                        colon = line.find(":", end_of_indent)
                        if colon == -1:
                            raise ValueError(f"No key: value on line {line_num}.")
                        key = CommentedChunk.from_line(CCMode.DICT_KEY, line[:colon+1], above)
                        above = ''
                        value = CommentedChunk.from_line(CCMode.DICT_VALUE, line[colon + 1:])
                        result[key] = value
                        prev_value = value
                        prev_key = key

class ListParser:
    def parse(self, start_at: ParsePoint) -> Tuple[CommentedList, ParsePoint]:
        """
        Implements a state machine to parse a list from a string. For docs on the state
        machine, see https://bit.ly/3OE2UJo.
        """
        above = start_at.above
        start_of_line = start_at.offset
        line_num = start_at.line_num
        data = start_at.data
        eof = len(data)
        result: CommentedList = CommentedList()

        while start_of_line < eof:
            end_of_indent, end_of_line, line = split_line(data, start_of_line, eof)
            raise_on_bad_indent(data, start_of_line, end_of_indent, line_num, start_at.indent, allow_nest=False)
            if end_of_indent == end_of_line:
                above += line + '\n'
            else:
                first_char = data[end_of_indent]
                if first_char == '#':
                    above += line
                else:
                    this_indent = end_of_indent - start_of_line
                    if this_indent == start_at.indent + 2:
                        if len(result) == 0:
                            raise ValueError(f"Premature indent on line {line_num}. Expected list item.")
                    elif this_indent > start_at.indent:
                        assert not "In theory, this should have been caught in raise_on_bad_intent"
                    elif this_indent < start_at.indent:
                        if above:
                            result[None] = CommentedChunk(CCMode.LAST_ITEM, above)
                        resume_at = ParsePoint(data, start_of_line, line_num, this_indent)
                        return result, resume_at
                    else:
                        if first_char == '-':
                            value = CommentedChunk.from_line(CCMode.LIST_VALUE, line[1:])
                            result.append(value)
                        else:
                            raise ValueError(f"Expected list item on line {line_num}.")

def load(data: str) -> dict:
    parser = DictParser()
    start_at = ParsePoint(data)
    result, _ = parser.parse(start_at)
    return result

def dump(data: dict) -> str:
    pass
"""