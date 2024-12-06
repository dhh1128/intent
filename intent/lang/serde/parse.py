from abc import ABC, abstractmethod
from enum import Enum
from typing import NamedTuple

from .code import Code
from .pieces import Dict, List, Chunk, Expansion

__all__ = ["load", "dump", "Value"]

def end_of_indent(data: str, i: int, end: int) -> tuple:
    while i < end:
        c = data[i]
        if c != ' ': break
        i += 1
    return i

def raise_on_bad_indent(data: str, start_of_line: int, end_of_indent: int, line_num: int, current_indent: int):
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

def find_char_in_escaped(txt: str, ch: str) -> int:
    skip_next = False
    for i, c in enumerate(txt):
        if skip_next:
            skip_next = False
            continue
        if c == ch:
            return i
        elif c == '\\':
            skip_next = True

class SplitLineTuple(NamedTuple):
    end_of_indent: int
    end_of_line: int

def split_line(data: str, i: int, eof: int) -> SplitLineTuple:
    eoi = end_of_indent(data, i, eof)
    eol = end_of_line(data, i, eof)
    return SplitLineTuple(eoi, eol)

class ParsePoint(NamedTuple):
    data: str
    start: int = 0
    line_num: int = 1
    indent: int = 0
    above: str = ''
    def advance(self, start: int, line_num: int, above: str = '') -> 'ParsePoint':
        return ParsePoint(self.data, start, line_num, self.indent, above)

class ParseResult(NamedTuple):
    code: Code
    point: ParsePoint

class Parser(ABC):
    parent: 'Parser'

    def __init__(self, parent: 'Parser' = None):
        self.parent = parent

    @abstractmethod
    def parse(self, start_at: ParsePoint) -> ParseResult:
        pass

class SkipAboveTuple(NamedTuple):
    start: int
    end_of_indent: int
    end_of_line: int
    line_num: int
    above: str

def skip_above(point: ParsePoint) -> SkipAboveTuple:
    """
    Advance to the next line that contains content, accumulating blank lines and
    comments so they can be attached to what comes next. If indent rules are
    violated in the process, raise a ValueError.
    """
    start_of_line = point.start
    line_num = point.line_num
    above = ''
    eof = len(point.data)
    while start_of_line < eof:
        end_of_indent, end_of_line = split_line(point.data, start_of_line, eof)
        raise_on_bad_indent(point.data, start_of_line, end_of_indent, line_num, point.indent)
        if end_of_indent == end_of_line:
            above += point.data[start_of_line:end_of_line] + '\n'
        else:
            if point.data[end_of_indent] == '#':
                above += point.data[start_of_line:end_of_line] + '\n'
            else:
                return SkipAboveTuple(start_of_line, end_of_indent, end_of_line, line_num, above)
        start_of_line = skip_eol(point.data, end_of_line, eof)
        line_num += 1

class UnknownContainerParser(Parser):
    def parse(self, start_at: ParsePoint) -> ParseResult:
        """
        Starts parsing what's inside a container without knowing what kind of container
        it is, and consumes just enough text to figure out whether to pass the job off
        to a DictParser or a ListParser.
        """
        above = start_at.above
        start_of_line = start_at.start
        line_num = start_at.line_num
        data = start_at.data

        start_of_line, end_of_indent, _, line_num, above = skip_above(
            start_at.advance(start_of_line, line_num))
        this_indent = end_of_indent - start_of_line
        if this_indent == start_at.indent:
            handoff_at = start_at.advance(start_of_line, line_num,above)
            first_char = data[end_of_indent]
            if first_char == '-':
                handoff_to = ListParser(self)
            else:
                handoff_to = DictParser(self)
            code, resume_at = handoff_to.parse(handoff_at)
            return code, resume_at
        elif this_indent < start_at.indent:
            # We found something other than a comment that is less indented than us,
            # so we're done parsing.
            code = Chunk.from_tail(above)
            resume_at = start_at.advance(start_of_line, line_num, above)
            return code, resume_at
        else:
            raise ValueError(f"Premature indent on line {line_num}.")

class DictParser(Parser):
    def parse(self, start_at: ParsePoint) -> ParseResult:
        """
        Implements a state machine to parse a dictionary from a string. For docs on the state
        machine, see https://bit.ly/3OE2UJo.
        """
        above = start_at.above
        start_of_line = start_at.start
        line_num = start_at.line_num
        data = start_at.data
        eof = len(data)
        result: Dict = Dict()
        prev_key: Chunk = None
        prev_value: Chunk = None

        while start_of_line < eof:
            start_of_line, end_of_indent, end_of_line, line_num, above = skip_above(
                start_at.advance(start_of_line, line_num))
            first_char = data[end_of_indent]
            if first_char == '-':
                raise ValueError(f"Expected key: value instead of list item on line {line_num}.")
            else:
                this_indent = end_of_indent - start_of_line
                if this_indent == start_at.indent:
                    line = data[start_of_line:end_of_line]
                    first_char = line[0]
                    colon = find_char_in_escaped(line, ':') if first_char in '\'"' else line.find(":")
                    if colon == -1:
                        raise ValueError(f"No key: value on line {line_num}.")
                    key = Chunk.from_dictkey(line[:colon+1], above)
                    above = ''
                    value = Chunk.from_dictvalue(line[colon + 1:])
                    result[key] = value
                    prev_value = value
                    prev_key = key
                elif this_indent == start_at.indent + 2:
                    if prev_value is None:
                        raise ValueError(f"Premature indent on line {line_num}. Expected key: value.")
                    nest_at = ParsePoint(data, start_of_line, line_num, this_indent, above)
                    above = ''
                    nest_to = UnknownContainerParser(self)
                    details, resume_at = nest_to.parse(nest_at)
                    expansion = Expansion(prev_value, details)
                    result[prev_key] = expansion
                    _, start_of_line, line_num, _, above = resume_at
                elif this_indent < start_at.indent:
                    if above:
                        result[None] = Chunk.from_tail(above)
                    resume_at = ParsePoint(data, start_of_line, line_num, this_indent)
                    return result, resume_at
                else: #this_indent > start_at.indent but not 2
                    assert not "In theory, this should have been caught in raise_on_bad_intent"
            start_of_line = skip_eol(data, end_of_line, eof)
            line_num += 1
        return result, start_at.advance(start_of_line, line_num, above)

class ListParser:
    def parse(self, start_at: ParsePoint) -> ParseResult:
        """
        Implements a state machine to parse a list from a string. For docs on the state
        machine, see https://bit.ly/3OE2UJo.
        """
        above = start_at.above
        start_of_line = start_at.start
        line_num = start_at.line_num
        data = start_at.data
        eof = len(data)
        result: List = List()

        while start_of_line < eof:
            start_of_line, end_of_indent, line_num, above = skip_above(
                start_at.advance(start_of_line, line_num))
            this_indent = end_of_indent - start_of_line
            if this_indent == start_at.indent:
                first_char = data[end_of_indent]
                if first_char == '-':
                    value = Chunk.from_listvalue(data[start_of_line + 1:end_of_line])
                    result.append(value)
                else:
                    raise ValueError(f"Expected list item on line {line_num}.")
            elif this_indent == start_at.indent + 2:
                if len(result) == 0:
                    raise ValueError(f"Premature indent on line {line_num}. Expected list item.")
                nest_at = ParsePoint(data, start_of_line, line_num, this_indent, above)
                above = ''
                nest_to = UnknownContainerParser(self)
                details, resume_at = nest_to.parse(nest_at)
                prev_value = result.pop()
                expansion = Expansion(prev_value, details)
                result.append(expansion)
                _, start_of_line, line_num, _, above = resume_at
            elif this_indent < start_at.indent:
                if above:
                    result[None] = Chunk.from_tail(above)
                resume_at = ParsePoint(data, start_of_line, line_num, this_indent)
                return result, resume_at
            else: #this_indent > start_at.indent but not 2
                assert not "In theory, this should have been caught in raise_on_bad_intent"
            start_of_line = skip_eol(data, end_of_line, eof)
            line_num += 1
        return result, start_at.advance(start_of_line, line_num, above)

def load(data: str) -> dict:
    parser = DictParser()
    start_at = ParsePoint(data)
    result, _ = parser.parse(start_at)
    return result

def dump(data: dict) -> str:
    pass
