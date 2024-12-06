from abc import ABC, abstractmethod
from enum import Enum
from typing import NamedTuple

from .pieces import Code, Dict, List, Chunk, first_two_tokens, first_non_space_char

__all__ = ["load", "dump", "Value"]

VALID_LIST_ITEM_BULLETS = ['-', '- ', '-\n', '-\r']

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
    def delta(self, start: int = None, line_num: int = None, indent: int = None, above: str = None) -> 'ParsePoint':
        return ParsePoint(self.data, 
                          self.start if start is None else start,
                          self.line_num if line_num is None else line_num, 
                          self.indent if indent is None else indent, 
                          self.above if above is None else above)

class ParseResult(NamedTuple):
    code: Code
    point: ParsePoint

class Parser(ABC):
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
            start_at.delta(start_of_line, line_num))
        this_indent = end_of_indent - start_of_line
        if this_indent == start_at.indent:
            clip = data[end_of_indent:end_of_indent + 2]
            if clip in VALID_LIST_ITEM_BULLETS:
                handoff_to = ListParser()
            else:
                handoff_to = DictParser()
            code, resume_at = handoff_to.parse(start_at)
            return code, resume_at
        elif this_indent < start_at.indent:
            # We found something other than a comment that is less indented than us,
            # so we're done parsing.
            code = Chunk.from_tail(above)
            resume_at = start_at.delta(start_of_line, line_num, above)
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
        first_line = True

        while start_of_line < eof:
            start_of_line, end_of_indent, end_of_line, line_num, above = skip_above(
                start_at.delta(start_of_line, line_num))
            this_indent = end_of_indent - start_of_line
            first_char = data[end_of_indent]
            line = None
            
            # DictParser normally consumes only lines that begin with as many spaces as its
            # indent. However, its first line requires special handling because a DictParser
            # might have be invoked by a ListParser that saw a list item that it determined
            # was a dictionary:
            #
            #   - key1:          <-------- a line like this
            #     key2: value
            #
            # In such a case, the first line that this parser encounters will begin with '-'
            # at the start, which we need to ignore. If we detect this condition, pretend
            # that we saw a normally indented line.
            if first_line:
                first_line = False
                # Did we detect an outdent (indent is 2 smaller than it should be)?
                if this_indent == start_at.indent - 2:
                    if data[end_of_indent:end_of_indent+2] in VALID_LIST_ITEM_BULLETS:
                        # The number of spaces after "-" is irrelevant, even though
                        # it should be one.
                        end_of_indent = first_non_space_char(data, end_of_indent + 2)
                        first_char = data[end_of_indent]
                        if end_of_indent > end_of_line: end_of_line = end_of_indent
                        # Treat us as normally indented despite the list item bullet.
                        this_indent = start_at.indent
                        line = ' '*this_indent + data[end_of_indent:end_of_line]

            if this_indent == start_at.indent:
                if first_char == '-':
                    raise ValueError(f"Expected key: value instead of list item on line {line_num}.")
                if line is None: # almost always true, except with weird first lines
                    line = data[start_of_line:end_of_line]
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
                nest_to = UnknownContainerParser()
                details, resume_at = nest_to.parse(nest_at)
                # Reinterpret the previous value as trailing text after key rather than a value.
                prev_key.post += str(prev_value)
                result[prev_key] = details
                _, start_of_line, line_num, _, above = resume_at
                continue
            elif this_indent < start_at.indent:
                if above:
                    result[None] = Chunk.from_tail(above)
                resume_at = ParsePoint(data, start_of_line, line_num, this_indent)
                return result, resume_at
            else: #this_indent > start_at.indent but not 2
                assert not "In theory, this should have been caught in raise_on_bad_intent"
            start_of_line = skip_eol(data, end_of_line, eof)
            line_num += 1
        return result, start_at.delta(start_of_line, line_num, above)

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
            start_of_line, end_of_indent, end_of_line, line_num, above = skip_above(
                start_at.delta(start_of_line, line_num))
            this_indent = end_of_indent - start_of_line
            if this_indent == start_at.indent:
                line = data[end_of_indent:end_of_line]
                handoff_to = None
                if line == '-':
                    line_num += 1
                    start_of_line = skip_eol(data, end_of_line, eof)
                    handoff_to = UnknownContainerParser()
                elif line.startswith('- '):
                    line = line[2:]
                    _, end_of_first_text = first_two_tokens(line)
                    if line.find(':', end_of_first_text) != -1:
                        handoff_to = DictParser()
                else:
                    raise ValueError(f"Expected list item on line {line_num}.")
                if not handoff_to:
                    value = Chunk.from_listvalue(line)
                    result.append(value)
                else:
                    new_indent = this_indent + 2
                    handoff_at = start_at.delta(start=start_of_line, line_num=line_num, indent=new_indent, above=above)
                    above = ''
                    value, resume_at = handoff_to.parse(handoff_at)
                    result.append(value)
                    _, start_of_line, line_num, _, above = resume_at
                    continue
            elif this_indent < start_at.indent:
                if above:
                    result[None] = Chunk.from_tail(above)
                resume_at = ParsePoint(data, start_of_line, line_num, this_indent)
                return result, resume_at
            else: #this_indent > start_at.indent
                assert not "In theory, this should have been caught in raise_on_bad_intent"
            start_of_line = skip_eol(data, end_of_line, eof)
            line_num += 1
        return result, start_at.delta(start_of_line, line_num, above)

def load(data: str) -> dict:
    parser = DictParser()
    start_at = ParsePoint(data)
    result, _ = parser.parse(start_at)
    return result

def dump(data: dict) -> str:
    pass
