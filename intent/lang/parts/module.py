import os
import weakref

from .fs import canonical_path

class Module:
    def __init__(self, path, space=None):
        self.path = canonical_path(path)
        self.folder, file = os.path.split(self.path)
        self._files = [file]
        self.name = file[:-2]
        self._space = weakref.ref(space) if space else None

    def files(self):
        return self._files

    @property
    def space(self):
        return self._space() if self._space else None

    @property
    def sid(self):
        """The identifier of this module, within its space."""
        s = self.space
        return s.abs_path_to_rel(self.path)[:-2] if s else None
    
    def compile(self):
        ast = {}
        return ast, None
