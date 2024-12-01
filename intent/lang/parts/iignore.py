import os
from typing import Optional
import pathspec

from .fs import canonical_path, enforced_canonical_folder

DOT_IGNORE_NAME = '.iignore'

DEFAULT_IIGNORE_HEADER = '''# Patterns for files and folders to exclude from intent's attention.
# Same syntax and rules, including hierarchy, as .gitignore (and rsync before
# it).

# Anything owned by git.
.git/
'''

DEFAULT_IGNORE_PATS = '''
# General OS and editor
.DS_Store
Thumbs.db
*.swp
*.swo
*.bak
*.tmp
~*

# IDE-specific files
.idea/
.vscode/
*.code-workspace
*.sublime-workspace
*.sublime-project
*.log

# Python
__pycache__/
*.py[cod]
*$py.class
env/
*.egg-info/
.eggs/
build/
dist/
.ipynb_checkpoints/
.cache/
*.pytest_cache/
htmlcov/
.coverage
.coverage.*
.mypy_cache/

# Rust
target/
*.rs.bk
*.profraw

# JavaScript / Node.js / React
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log
.eslintcache
.next/
out/
dist/
coverage/

# React Native
ios/
android/
*.xcworkspace/
*.xcodeproj/
*.gradle/
*.apk
*.keystore

# Java
*.class
*.jar
*.war
*.ear
*.iml
*.log
target/
.gradle/
build/
.project
.classpath
.settings/
bin/

# Go
*.exe
*.dll
*.so
*.dylib
bin/
*.test
go.sum
*.out

# Additional Coverage Tools
lcov-report/
*.lcov
'''

DEFAULT_IIGNORE = DEFAULT_IIGNORE_HEADER + DEFAULT_IGNORE_PATS
DEFAULT_GITIGNORE = DEFAULT_IGNORE_PATS

def normalize_path_for_git(fpath:str) -> str:
	"""
	Roughly, a copy of the normalize_file function in util.py in pathspec.
    We copy it because we need to call it directly, in our test_path() func
    that basically overrides GitIgnoreSpec.match_file(). Unfortunately, this
    function isn't exposed for import by the pathspace library. We can actually
    simplify it anyway; we know what separator is going to be present in our paths.
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
    def __init__(self, path: str):
        self.path: str = canonical_path(path)
        self._spec: Optional[pathspec.GitIgnoreSpec] = None
        self._mtime = None

    @property
    def spec(self) -> pathspec.GitIgnoreSpec:
        current_mtime = os.path.getmtime(self.path)
        if self._spec is None or self._mtime < current_mtime:
            with open(self.path, 'r') as f:
                self._spec = pathspec.GitIgnoreSpec.from_lines(f)
            self._mtime = current_mtime
        return self._spec
    
    def test_path(self, path: str) -> Optional[bool]:
        """
        Decide if a path matches one of the defined pattern or not. Returns True
        if the path should be ignored because it matches a normal pattern (e.g., *.txt),
        False if it should be affirmatively included because it matches a negated pattern
        (e.g., !*.txt), or None if the file doesn't match a pattern at all (meaning it
        will be False unless we find an affirmative match in another DotIIgnore at a
        higher level in the directory tree.
        """
        std_path = normalize_path_for_git(path)
        match, _index = self.spec._match_file(enumerate(self.spec.patterns), std_path)
        return match
    
class HierarchicalDotIIgnore:
    def __init__(self, root: str):
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

