import datetime
import os
import re
import uuid

OUT_PAT = re.compile(r'^[\t ]*out/', re.MULTILINE)

from .fs import canonical_path, enforced_canonical_folder, folders_back_to_root
from .iignore import DOT_IGNORE_NAME, DEFAULT_IIGNORE, DEFAULT_GITIGNORE

DEFAULT_SPACE_I = '''# Define properties of this space.
id: {space_id}
when_inited: !!timestamp {timestamp}
'''

def any(_):
    """Used as default arg for match_files, match_dirs, and recurse_dirs; matches everything.""" 
    return True

class Space:
    """
    Represents the main unit of code organization for intent. Generally maps directly to
    a project and a git repository.
    """
    def __init__(self, path: str) -> None:
        self.path = enforced_canonical_folder(path)
        self._ignores = None

    @property
    def name(self) -> str:
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

    def abs_path_to_rel(self, abs_path: str) -> str:
        return "/" + os.path.relpath(abs_path, self.path)

    def rel_path_to_abs(self, rel_path: str) -> str:
        return canonical_path(os.path.join(self.path, rel_path))
    
    @staticmethod
    def find_root(path: str = '.') -> str:
        """
        Find the root of the space that contains the given path. If the path
        is not in a space, None is returned.
        """
        for containing_folder in folders_back_to_root('path'):
            if Space.is_space(containing_folder):
                return containing_folder
        return None
    
    @staticmethod
    def is_space(path: str) -> bool:
        """
        Determine if the given path is the root of a space.
        """
        return os.path.isfile(os.path.join(path, 'space.i'))

    @staticmethod
    def init(folder: str, force=False) -> 'Space':
        """
        Initialize a new space in the given folder. The folder must exist. Normally,
        correct behavior would be to init a folder that is also a git repo. An
        error will be thrown if a git repo is detected in an ancestor folder of the
        specified location, unless ignore_git is set to True.
        """
        if not os.path.exists(folder):
            raise ValueError(f'Folder does not exist: {folder}')
        if os.path.isfile(folder):
            raise ValueError(f'Not a folder: {folder}')
        if not force:
            for containing_folder in folders_back_to_root(folder):
                dot_git = os.path.join(containing_folder, '.git');
                if os.path.isdir(dot_git):
                    if containing_folder == folder:
                        break
                    raise ValueError(f'Not initing at root of git repo ({containing_folder}).')
        space = Space(folder)
        gitignore = space.rel_path_to_abs('.gitignore')
        if not os.path.exists(gitignore):
            with open(gitignore, 'wt') as f:
                f.write(DEFAULT_GITIGNORE)
        iignore = space.rel_path_to_abs(DOT_IGNORE_NAME)
        if not os.path.exists(iignore):
            with open(iignore, 'wt') as f:
                f.write(DEFAULT_IIGNORE)
        out_folder = space.rel_path_to_abs('out')
        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
        space_i = space.rel_path_to_abs('space.i')
        if not os.path.exists(space_i):
            with open(space_i, 'wt') as f:
                timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                content = DEFAULT_SPACE_I.format(space_id=uuid.uuid4(), timestamp=timestamp)
                f.write(content)
        return space
    
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
