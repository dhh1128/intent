import ast
import warnings
import re

INVALID_ESC_SEQ_PAT = re.compile(r"invalid escape sequence [\"']\\.[\"']")
DICT_KEY = 0
DICT_VALUE = 1
LIST_VALUE = 2
LAST_ITEM = 3
COMMENTEDVALUE_MODES = [DICT_KEY, DICT_VALUE, LIST_VALUE, LAST_ITEM]

__all__ = ["CommentedChunk", "CommentedList", "CommentedDict", "DICT_KEY", "DICT_VALUE", "LIST_VALUE", "LAST_ITEM"]

def index_first_non_space_char(s):
    for i, c in enumerate(s):
        if c != " ":
            return i

def safe_literal_eval(s):
    """
    Evaluates a Python string literal safely, suppressing SyntaxWarnings.
    This suppression is necessary because such warnings are not derived from
    Exception and are thus designed to written to stderr by the python compiler,
    independent of a program's error handling strategy.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)  # Suppress SyntaxWarning
        try:
            return ast.literal_eval(s)
        except (ValueError, SyntaxError, SyntaxWarning) as e:
            txt = str(e)
            m = INVALID_ESC_SEQ_PAT.search(str(e))
            if m:
                raise ValueError(m.group())
            else:
                raise ValueError(txt)
            
def beginning_of_left_pad_before(line, i):
    """
    Given a line like abc  : def, and the offset of :,
    find the first space char after abc.
    """
    j = i - 1
    while j >= 0 and line[j] == ' ':
        j -= 1
    return j + 1
        
class CommentedChunk:
    """
    Represent a single chunk of text that may be preceded by an "above" (one or more
    blank lines or comments and an optional "pre" (leading spaces on the same line) --
    and that may be followed by a "divider" + "post" (spaces and a comment on the same
    line) and a "below" (one or more blank lines or comments on subsequent lines.

    This is the data type used as a key in CommentedDict, where it ends at the colon in
    a key: value line, pre is the indent, and chunk is followed by divider (the colon),
    but never by post or below. In such a case, the mode of the chunk is DICT_KEY:

        above
        pre chunk divider         (divider always holds a colon)

    This is also the data type used as a value in a CommentedDict, where it begins after
    the colon, pre is space between the colon and the value, and value is never preceded
    by above or followed by below. In such a case, the mode of the chunk is DICT_VALUE:

        pre chunk divider post    (if present, post is a comment, divider must not be None)

    It is also the data type used as a value in a CommentedList, where it can have all
    of its properties. In such a case, the mode of the chunk is LIST_VALUE:

        above
        pre chunk divider post

    If an intent module file ends with comments or blank lines (either inside a dict or
    a list), these are stored in a CommentedValue with only above -- no pre, chunk,
    divider, or post. It is the last item in the CommentedDict. In such a case, the mode
    of the chunk is LAST_ITEM:

        above
    
    A chunk may be double- or single-quoted. If it is, the open quote is the last char
    of pre, the close quote is the first char of divider, and the value of chunk is
    interpreted by replacing python escape sequences with their corresponding characters.
    (The .escaped_chunk property gives the text with backslashes interpreted literally.)
    This lets chunk logically hold \n, \t, :, # (with \x3a and \x23, respectively).
    Without this support, : and # would otherwise end the chunk. Quoted chunks also let
    us distinguish between ~ or null as a chunk value (representing the null value) and
    "~" or "null" (representing the literal string equivalents).

    The str value of a CommentedChunk is the chunk by itself, disregarding all other
    properties.
    """
    def __init__(self, mode: int, above: str = None, pre: str = None, chunk: str = None, 
                 divider: str = None, post: str = None):
        """
        Initialize a CommentedChunk.
        
        For quoted chunks, pass chunk with the surrounding quote
        chars; self.pre becomes pre + quote char, self.divider becomes quote char + divider,
        and self.chunk becomes the inner chunk value with all escape sequences resolved. If
        post is not None, divider MUST also not be None.

        If mode is None, it is guessed based on the presence of above, post, and below.

        Raises a ValueError if preconditions are not met, if a quoted chunk has invalid syntax,
        or if args don't match mode.
        """
        # Check mode-related preconditions.
        if mode not in COMMENTEDVALUE_MODES:
            raise ValueError(f"Invalid mode {mode}.")
        if not divider:
            if mode == DICT_KEY:
                raise ValueError("Mode can't be DICT_KEY without : in divider.")
            if above:
                if not chunk and not pre and not post:
                    if mode != LAST_ITEM:
                        raise ValueError("With only above, mode must be LAST_ITEM.")
            else:
                if not chunk and not pre and not post:
                    raise ValueError("Can't be empty of all content.")
            if post:
                if divider is None: # instead of empty string...
                    raise ValueError("Can't have post without divider.")
        else:
            if ":" in divider:
                if mode != DICT_KEY:
                    raise ValueError("Mode must be DICT_KEY with : in divider.")
            else:
                if above:
                    if mode != LIST_VALUE:
                        raise ValueError("Mode must be LIST_VALUE with above but not : in divider.")
                elif mode == DICT_KEY:
                    raise ValueError("Mode can't be DICT_KEY without : in divider.")
        # Do special handling of chunk, which might be quoted and escaped.
        if chunk:
            first_chunk_char = chunk[0]
            if first_chunk_char in '\'"':
                if chunk[-1] != first_chunk_char:
                    raise ValueError("unbalanced quotes on chunk.")
                self.chunk = chunk
                try:
                    self.interpreted_chunk = safe_literal_eval(chunk)
                except SyntaxWarning as e:
                    raise ValueError(e)
                pre = first_chunk_char if pre is None else pre + first_chunk_char
                divider = first_chunk_char if divider is None else first_chunk_char + divider
            else:
                self.interpreted_chunk = self.chunk = chunk
        else:
            self.interpreted_chunk = self.chunk = ""
        self.above = above if above is not None else ""
        self.pre = pre if pre is not None else ""
        self.divider = divider if divider is not None else ""
        self.post = post if post is not None else ""
        self.mode = mode

    @property
    def quote_char(self):
        return self.pre[-1] if self.pre[-1] in '\'"' else None

    @staticmethod
    def from_line(mode: int, line: str, above: str = ""):
        """
        Convenience method that parses a line into pre, chunk, divider, and post.

        If mode == DICT_KEY, pre is the indent, chunk is the key, and divider is the colon.
        We will never have divider or post.
        
        If mode == DICT_VALUE, pre is the space between the colon and the value, chunk is
        the value, and we might have divider+post (space before comment, comment).
        
        If mode == LIST_VALUE, pre is the indent, chunk is the value, and we might have
        divider+post (space before comment, comment).
        """
        pre_offset = index_first_non_space_char(line)
        pre = line[:pre_offset]
        if mode == DICT_KEY:
            i = line.find(":", pre_offset)
            if i == -1:
                raise ValueError("No : found in line.")
            # divider should be any spaces before :, plus the : char itself
            divider_begin = beginning_of_left_pad_before(line, i)
            divider = line[divider_begin:i+1]
            return CommentedChunk(above=above, pre=pre, chunk=line[pre_offset:divider_begin], divider=divider, mode=mode)
        else:
            i = line.find("#", pre_offset)
            if i == -1:
                # divider should be any spaces between the end of the value and the end of line
                divider_begin = beginning_of_left_pad_before(line, len(line))
                divider = line[divider_begin:]
                return CommentedChunk(above=above, pre=pre, chunk=line[pre_offset:divider_begin], divider=line[divider_begin:], mode=mode)
            else:
                # divider should be any spaces between the end of the value and the # of the comment
                divider_begin = beginning_of_left_pad_before(line, i)
                divider = line[divider_begin:i]
                return CommentedChunk(above=above, pre=pre, chunk=line[pre_offset:divider_begin], divider=line[divider_begin:i], post=line[i:], mode=mode)
        
    @property
    def text(self):
        return self.above + self.pre + self.chunk + self.divider + self.post

    def __str__(self):
        return self.interpreted_chunk

    def __repr__(self):
        return str(self)
    
    def __eq__(self, value: object) -> bool:
        return self.interpreted_chunk == value

class CommentedList(list):
    def __init__(self, *args):
        super().__init__(*args)

    @property
    def text(self):
        """
        Returns a string representation of the list, including comments.
        """
        return "\n".join(item.text if isinstance(item, CommentedChunk) else str(item) for item in self)

class CommentedDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Store comments associated with keys
        self._comments = {}

    @property
    def text(self):
        """
        Returns a string representation of the dict, including comments.
        """
        lines = []
        for key, value in self.items():
            ktext = key.text if isinstance(key, CommentedChunk) else key
            lines.append(f"{ktext}: {value.text if isinstance(value, CommentedChunk) else value}")
        return "\n".join(lines)
