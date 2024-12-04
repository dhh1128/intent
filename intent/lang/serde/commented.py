__all__ = ["CommentedList", "CommentedValue"]

def first_non_space_char(s):
    for c in s:
        if c != " ":
            return c
        
class CommentedValue:
    """
    Represent a single value that may be preceded by a head (one or more full-line comments),
    and followed by a tail (an inline comment at the end).
    """
    def __init__(self, value, head: str = "", tail: str = "", divider=" "):
        self.value = value
        self.head = head
        self.divider = divider
        self.tail = tail

    @staticmethod
    def from_line(line: str, head: str = ""):
        i = line.find("#")
        if i == -1:
            return CommentedValue(line[:j], head=head)
        else:
            # Find the first char that isn't part of the value
            j = i - 1
            while line[j] == ' ' and j >= 0:
                j -= 1
            j += 1
            return CommentedValue(line[:j], head=head, tail=line[i:], divider=line[j:i])
        
    @property
    def text(self):
        if self.head:
            if self.tail:
                return f"{self.head}\n{self.value}{self.divider}{self.tail}"
            else:
                return f"{self.head}\n{self.value}"
        else:
            if self.tail:
                return f"{self.value}{self.divider}{self.tail}"
            else:
                return str(self.value)

    def __str__(self):
        return self.value

    def __repr__(self):
        return str(self)
    
    def __eq__(self, value: object) -> bool:
        return self.value == value

class CommentedList(list):
    def __init__(self, *args):
        super().__init__(*args)

    @property
    def text(self):
        """
        Returns a string representation of the list, including comments.
        """
        return "\n".join(item.text if isinstance(item, CommentedValue) else str(item) for item in self)

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
            ktext = key.text if isinstance(key, CommentedValue) else key
            lines.append(f"{ktext}: {value.text if isinstance(value, CommentedValue) else value}")
        return "\n".join(lines)
