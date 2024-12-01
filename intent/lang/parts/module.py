import os
import weakref

from .space import Space
from .fs import canonical_path




class Module:
    def __init__(self, path, space: Space=None):
        path = canonical_path(path)
        if path.endswith('.i'):
            self.pre = path[:-2]
        self.path = path
        self._space = weakref.ref(space) if space else None
    
    @property
    def name(self):
        return os.path.split(self.path)[1][:-2]

    @property
    def space(self):
        return self._space() if self._space else None

    @property
    def rel_path(self):
        s = self.space
        return s.abs_path_to_rel(self.path) if s else None
