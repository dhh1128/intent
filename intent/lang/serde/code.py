from abc import ABC, abstractmethod

class Code(ABC):
    """A construct that can be converted to code."""
    @property
    @abstractmethod
    def code(self) -> str:
        """Return this construct and all its surrounding text, as it appears in code."""
        pass

