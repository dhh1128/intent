from .commented import CommentedDict, CommentedList, CommentedChunk

__all__ = ["load", "dump", "Value"]

def parse_indent(data: str, offset: int, end: int, line_num: int, last_indent: int) -> tuple:
    i = offset
    while i < end:
        c = data[i]
        if c != ' ': break
        i += 1
    indent = i - offset
    if c == '\t':
        raise ValueError(f"Invalid indent (tab) on line {line_num}. Only 2-space indents are allowed.")
    elif indent % 2 == 1:
        raise ValueError(f"Bad indent ({indent} spaces) on line {line_num}. Only 2-space indents are allowed.")
    elif indent > last_indent + 2:
        raise ValueError(f"Too indented ({indent} spaces) on line {line_num}. Expected max {last_indent + 2}.")
    else:
        return i
def load(data: str) -> dict: pass
def dump(data: dict) -> str: pass
class Value: pass
"""
    result = {}
    nested = [result]
    obj = None
    line_num = 0
    last_indent = 0
    last_key = None
    head = None
    line_start = 0
    end = len(data)
    while line_start < end:
        line_num += 1
        line_end = data.find("\n", line_start)
        if line_end == -1: line_end = end
        line = data[line_start:line_end + 1]
        # Analyze leading whitespace and complain if something's wrong with it.
        end_of_indent = parse_indent(line, line_start, end, line_num, last_indent)
        if end_of_indent == end: # line of pure spaces
            head += line
        else:
            c = data[end_of_indent]
            indent = end_of_indent - line_start
            # comment or empty line ?
            if c in "#\r": 
                head += line
            # list item?
            elif c == '-':
                if isinstance(obj, dict):
                    raise ValueError(f"Expected key: value instead of list item on line {line_num}.")
                if indent == last_indent:
                    # If this is the first item in the list, pop last obj from stack.
                    if obj is None:
                        obj = nested.pop()
                        if isinstance(obj, CommentedChunk): pass
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
                    raise ValueError(f"No key: value on line {line_num}.")
                key = CommentedChunk.from_line(line[:colon], head)
                value = CommentedChunk.from_line(line[colon + 1:])
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
        line_start = line_end + 1
    return result

def dump(data: dict) -> str:
    pass
"""