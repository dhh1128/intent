import os
from typing import Optional
import pathspec

__all__ = ['Space', 'HierarchicalDotIIgnore', 'DOT_IGNORE_NAME']

DOT_IGNORE_NAME = '.iignore'

def canonical_path(path):
    """
    Expands references to user's home dir, converts relative to absolute,
    normalizes separators to os.path.sep, removes redundant and trailing
    separators. Does not resolve symlinks. 
    """
    if path.startswith('~'):
        path = os.path.expanduser(path)
    return os.path.abspath(os.path.normpath(path))

def enforced_canonical_folder(path):
    path = canonical_path(path)
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise ValueError(f'Not a folder: {path}')
    return path

def git_normalize_file(fpath:str) -> str:
	"""
	Roughly, a copy of the normalize_file function in util.py in pathspec.
    We copy it because it's not exposed for import by the pathspace module,
    and we can actually simplify it anyway; we know what separator is going
    to be present in our paths.
	"""
	norm_file = fpath.replace(os.path.sep, '/')
	if norm_file.startswith('/'):
		norm_file = norm_file[1:]
	elif norm_file.startswith('./'):
		norm_file = norm_file[2:]
	return norm_file
    
class DotIIgnore:
    """
    Provide support for .iignore files, more or less paralleling the
    behavior of git with .gitignore.
    """
    def __init__(self, path):
        self.path: str = canonical_path(path)
        self._spec: Optional[pathspec.GitIgnoreSpec] = None
        self._mtime = None

    @property
    def spec(self):
        current_mtime = os.path.getmtime(self.path)
        if self._spec is None or self._mtime < current_mtime:
            with open(self.path, 'r') as f:
                self._spec = pathspec.GitIgnoreSpec.from_lines(f)
            self._mtime = current_mtime
        return self._spec
    
    def test_path(self, path) -> Optional[bool]:
        """
        Decide if a path matches one of the defined pattern or not. Returns True
        if the path should be ignored because it matches a normal pattern (e.g., *.txt),
        False if it should be affirmatively included because it matches a negated pattern
        (e.g., !*.txt), or None if the file doesn't match a pattern at all (meaning it
        will be False unless we find an affirmative match in another DotIIgnore at a
        higher level in the directory tree.
        """
        std_path = git_normalize_file(path)
        match, _index = self.spec._match_file(enumerate(self.spec.patterns), std_path)
        return match
    
class HierarchicalDotIIgnore:
    def __init__(self, root):
        self.root = enforced_canonical_folder(root)
        self._iignores = None # lazy init

    @property
    def iignores(self):
        """
        Returns a dictionary of DotIgnore objects, keyed by the directory they're in.
        """
        if self._iignores is None:
            self._iignores = {}
            for root, _, files in os.walk(self.root):
                if DOT_IGNORE_NAME in files:
                    path = os.path.join(root, DOT_IGNORE_NAME)
                    self._iignores[root] = DotIIgnore(path)
        return self._iignores
    
    def test_path(self, path)-> Optional[bool]:
        """
        Decide if a path matches one of the defined pattern or not. Returns True
        if the path should be ignored because it matches a normal pattern (e.g., *.txt),
        False if it should be affirmatively included because it matches a negated pattern
        (e.g., !*.txt), or None if the file doesn't match a pattern at all (meaning it
        will be False unless we find an affirmative match in another DotIIgnore at a
        higher level in the directory tree.
        """
        if not self.iignores:
            return False
        path = canonical_path(path)
        if os.path.commonpath([path, self.root]) != self.root:
            return False
        min_len = len(self.root)
        current = path
        while len(path) > min_len:
            iignore = self._find_governing_iignore(current)
            if not iignore:
                break
            result = iignore.test_path(path)
            if result is not None:
                return result
            current = os.path.dirname(iignore.path)
        return None
    
    def _find_governing_iignore(self, path):
        # It only makes sense to attempt matches if the path is within the root.
        try:
            if os.path.commonpath([path, self.root]) == self.root:
                min_len = len(self.root)
                while len(path) > min_len:
                    parent = os.path.dirname(path)
                    di = self.iignores.get(parent)
                    if di: 
                        return di
                    path = parent
        except ValueError: 
            pass # Paths are a mixture of relative and absolute, or are on different drives.
        return None

def any(item):
    """Used as default arg for match_files, match_dirs, and recurse_dirs; matches everything.""" 
    return True

class Space:
    """
    Represents the main unit of code organization for intent. Generally maps directly to
    a project and a git repository.
    """
    def __init__(self, path) -> None:
        self.path = enforced_canonical_folder(path)
        self._ignores = None

    @property
    def name(self):
        return os.path.basename(self.path)
    
    @property
    def ignores(self):
        if self._ignores is None:
            for _, _, files in self.walk(self.path):
                if DOT_IGNORE_NAME in files:
                    with open(os.path.join(root, DOT_IGNORE_NAME)) as f:
                        for line in f:
                            yield line.strip()
        return self._ignores
    
    def should_ignore(self, item_name):
        return False
    
    def compile(self):
        """
        Compile the space into a form that can be used by the intent engine.
        """
        pass
    
    def walk(self, topdown=True, onerror=None, followlinks=False, 
             match_file=any, match_dir=any, recurse_dir=any, 
             include_ignored=False):
        """
        Walk the space. This is a convenience method that wraps os.walk.
        It always starts from the root of the space. It is aware of .iignore
        files, and it provides easy filtering and control over recursion.
        """
        ignore = lambda x: False if include_ignored else self.should_ignore
        for root, dirs, files in os.walk(self.abspath, topdown=topdown, onerror=onerror, followlinks=followlinks):
            if match_file is not None and match_file is not any:
                files[:] = [f for f in files if match_file(f)]
            # We use dirs for two different things: to return a list of dirs, and
            # to control recursion. We can't just modify dirs in place here, because
            # we need to start with an unmodified version of it at the bottom, when we're
            # recursing. So if we're going to modify the list, make a copy first.
            if match_dir is not None and match_dir is not any:
                matched_dirs = [d for d in dirs if match_dir(d)]
            else:
                matched_dirs = dirs
            yield root, [d for d in matched_dirs if not ignore(d)], [f for f in files if not ignore(f)]
            # Prune the recursion as requested.
            dirs[:] = [d for d in dirs if recurse_dir(d) and not ignore(d)]
