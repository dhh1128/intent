import os
from intent.lang.parts.fs import canonical_path, enforced_canonical_folder, folders_back_to_root

from .util import temp_folder

def test_canonical_path_expand_user():
    # Test case 1: Path starts with '~'
    path = '~/documents/file.txt'
    expected = os.path.abspath(os.path.expanduser(path))
    assert canonical_path(path) == expected

def test_canonical_path_already_absolute():
    # Test case 2: Path is already absolute
    path = '/home/daniel/code/intent'
    expected = os.path.abspath(path)
    assert canonical_path(path) == expected

def test_canonical_path_relative():
    # Test case 3: Path is relative
    path = '../documents/file.txt'
    expected = os.path.abspath(path)
    assert canonical_path(path) == expected

def test_canonical_path_redundant_separators():
    # Test case 4: Path contains redundant separators
    path = '/home/daniel/code/intent//lang/parts/fs.py'
    expected = os.path.abspath(path)
    assert canonical_path(path) == expected

def test_canonical_path_trailing_sep():
    # Test case 5: Path ends with a trailing separator
    path = '/home/daniel/code/intent/'
    expected = os.path.abspath(path.rstrip(os.path.sep))
    assert canonical_path(path) == expected
    
def test_enforced_canonical_folder_on_existing_folder():
    # Test case 1: Path is a folder
    path = os.path.dirname(__file__)
    expected = canonical_path(path)
    assert enforced_canonical_folder(path) == expected

def test_enforced_canonical_folder_on_existing_file():
    # Test case 2: Path is a file
    path = __file__
    try:
        enforced_canonical_folder(path)
        assert False, f"Expected ValueError for path: {path}"
    except ValueError as e:
        assert 'Not a folder' in str(e)

def test_enforced_canonical_folder_on_subset_is_existing_file():
    # Test case 2: Path is a file
    path = os.path.join(__file__, 'subdir')
    try:
        enforced_canonical_folder(path)
        assert False, f"Expected ValueError for path: {path}"
    except ValueError as e:
        assert 'Not a folder' in str(e)

def test_enforced_canonical_folder_on_valid_subset():
    # Test case 3: Path does not exist
    path = os.path.join(os.path.dirname(__file__), 'nonexistent')
    # Should not raise exception...
    enforced_canonical_folder(path)
        
def test_enforced_canonical_folder_on_folder_symlink(temp_folder):
    os.makedirs(os.path.join(temp_folder.path, 'real'))
    os.symlink('real', os.path.join(temp_folder.path, 'link'))
    symlink_path = os.path.join(temp_folder.path, 'link', 'subdir')
    os.makedirs(symlink_path)
    # Should not raise exception...
    ecf = enforced_canonical_folder(symlink_path)
    assert ecf.endswith('link/subdir')

def test_enforced_canonical_folder_on_file_symlink(temp_folder):
    real_path = os.path.join(temp_folder.path, 'real')
    with open(real_path, 'wt') as f:
        f.write('content')
    symlink_path = os.path.join(temp_folder.path, 'link')
    os.symlink('real', symlink_path)
    try:
        enforced_canonical_folder(symlink_path)
        assert False, f"Expected ValueError for path: {path}"
    except ValueError as e:
        assert 'Not a folder' in str(e)

def test_folders_back_to_root_on_file():
    # Test case 1: Path is a file
    path = canonical_path(__file__)
    items = list(folders_back_to_root(path))
    assert len(items) >= 4
    assert items[0] == os.path.dirname(path)
    assert items[-1] != items[-2]

def test_folders_back_to_root_on_folder():
    # Test case 2: Path is a folder
    path = os.path.dirname(canonical_path(__file__))
    items = list(folders_back_to_root(path))
    assert len(items) >= 4
    assert items[0] == path
