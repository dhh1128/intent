from typing import NamedTuple
from commented import CommentedDict, CommentedList, CommentedValue

__all__ = ["load", "dump", "Value"]


class Value:
    def __init__(self, value, meta=None, comment=None):
        self.value = value
        self.meta = meta
        self.comment = comment

    @property
    def is_list(self):
        return isinstance(self.value, list)
    
    @property
    def is_dict(self):
        return isinstance(self.value, dict)
    
    @property
    def is_primitive(self):
        return not (self.is_list or self.is_dict)
    
    def __str__(self):
        txt = str(self.meta) + " " if self.meta else ""
        if self.is_primitive:
            txt += str(self.value)
        if self.comment:
            txt += self.comment
        if self.is_list:
            sep = "\n  - "
            txt += sep + sep.join([str(v) for v in self.value])
        elif self.is_dict:
            sep = "\n  "
            txt += sep + sep.join([f"{k}: {v}" for k, v in self.value.items()])
        return txt
    
class KeyValuePair(NamedTuple):
    key: str
    value: Value

def parse_leading_whitespace(line: str, line_num, last_indent) -> tuple:
    for i, c in enumerate(line):
        if c != ' ':
            break
    if c == '\t':
        raise ValueError(f"Invalid indent (tab) on line {line_num}. Only 2-space indents are allowed.")
    elif i % 2 == 1:
        raise ValueError(f"Bad indent ({i} spaces) on line {line_num}. Only 2-space indents are allowed.")
    elif i > last_indent + 2:
        raise ValueError(f"Too indented ({i} spaces) on line {line_num}. Expected max {last_indent + 2}.")
    else:
        return i
    
def load(data: str) -> dict:
    result = {}
    nested = [result]
    obj = None
    line_num = 0
    last_indent = 0
    last_key = None
    for line in data.split("\n"):
        line_num += 1
        if not line: continue
        # Consume whitespace and complain if something's wrong with it.
        indent = parse_leading_whitespace(line, line_num, last_indent)
        c = line[indent]
        if c == "#": 
            continue
        elif c in "\r\n": 
            continue
        elif c == '-':
            if obj is None or isinstance(obj, dict):
                raise ValueError(f"Unexpected list item on line {line_num}.")
            if indent == last_indent:
                if obj is None: obj = nested.pop() # first key:value pair for this obj
                if isinstance(obj, list):
                    obj.append({key: value})
                obj[key] = value
            elif indent == last_indent + 2:
                if obj is None:
                    raise ValueError(f"Premature indent on line {line_num}.")
                if c == '-':
                    if not isinstance(obj[last_key], list):
                        obj[last_key] = []
                    obj[last_key].append(value)
                else:
                    obj.append(line[indent + 1:].lstrip())
        else:
            colon = line.find(":", indent)
            if colon == -1:
                raise ValueError(f"No key: value pattern on line {line_num}.")
            key = line[indent:colon].rstrip()
            value = line[colon + 1:].lstrip()
            if indent == last_indent:
                if obj is None: obj = nested.pop() # first key:value pair for this obj
                if isinstance(obj, list):
                    obj.append({key: value})
                obj[key] = value
            elif indent == last_indent + 2:
                if obj is None:
                    raise ValueError(f"Premature indent on line {line_num}.")
                if c == '-':
                    if not isinstance(obj[last_key], list):
                        obj[last_key] = []
                    obj[last_key].append(value)
                else:
                    container = {}
                    obj[last_key] = container
                obj = container
                nested.append(obj)
                obj[key] = value
            else:
                while indent < last_indent:
                    obj = nested.pop()
                    last_indent -= 2
                obj[key] = value
            last_key = key
    return result

def dump(data: dict) -> str:
    pass