import os
from typing import Generator

def canonical_path(path: str) -> str:
    """
    Expands references to user's home dir, converts relative to absolute,
    normalizes separators to os.path.sep, removes redundant and trailing
    separators. This means that folders are returned without a trailing
    slash. Does not resolve symlinks. 
    """
    if path.startswith('~'):
        path = os.path.expanduser(path)
    return os.path.abspath(os.path.normpath(path))

def enforced_canonical_folder(path: str) -> str:
    """
    Returns the canonical version of the given path, which is intended to identify
    a folder. The result will always be safe to pass to os.makedirs.
    
    The enforcemet mechanism is that, if the path or any subset exists and is not a
    folder or a link to a folder, this function raises a ValueError.
    """
    path = canonical_path(path)
    # Find the longest subset of the path that points to something
    # that already exists.
    subset = path
    while not os.path.exists(subset):
        shorter = os.path.dirname(subset)
        # Stop when we don't get a shorter subset.
        if shorter == subset or (not shorter):
            break
        else:
            subset = shorter
    if os.path.exists(subset):
        if not os.path.isdir(subset):
            raise ValueError(f'Not a folder: {subset}')
    return path

def folders_back_to_root(path: str) -> Generator[str, None, None]:
    """
    Yield folders from the given path back to the root of the file system.
    The initial path can be either a file or folder; either way, the first value
    is the folder for the initial path. 
    """
    path = canonical_path(path)
    if os.path.isfile(path):
        path = os.path.dirname(path)
    while True:
        yield path
        parent = os.path.dirname(path)
        if parent == path:
            break
        path = parent

