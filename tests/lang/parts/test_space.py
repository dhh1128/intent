import os
import pytest
import shutil

from intent.lang.parts import Space, HierarchicalDotIIgnore

from .util import DATA_DIR, SPACE1_DIR, temp_folder

@pytest.fixture
def space1():
    return Space(SPACE1_DIR)

def test_name_from_folder_existing(space1):
    assert space1.name == 'space1'

def test_path_from_folder_abspath_existing(space1):
    assert space1.path == SPACE1_DIR

def test_name_from_folder_non_existing():
    s = Space('non_existing')
    assert s.name == 'non_existing'

def test_path_from_folder_weird_path_existing():
    s = Space(os.path.join(DATA_DIR, 'space1', '../../data/space1'))
    assert s.path == SPACE1_DIR

def test_name_from_folder_non_existing():
    s = Space('non_existing')
    assert s.name == 'non_existing'

ITEMS_CREATED_DURING_INIT = ['.iignore', '.gitignore', 'out', 'space.i']

def test_init_in_empty_folder(temp_folder):
    s = Space.init(temp_folder.path)
    for item in ITEMS_CREATED_DURING_INIT:
        assert os.path.exists(os.path.join(temp_folder.path, item))

def test_init_idempotent(temp_folder):
    for i in range(len(ITEMS_CREATED_DURING_INIT)):
        s1 = Space.init(temp_folder.path)
        # Delete one of the starting artifacts.
        path = s1.rel_path_to_abs(ITEMS_CREATED_DURING_INIT[i])
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)
        # Call init again; see if it restores the missing artifact.
        s2 = Space.init(temp_folder.path)
        for item in ITEMS_CREATED_DURING_INIT:
            assert os.path.exists(os.path.join(temp_folder.path, item))

def test_init_below_git_repo_root_fails_without_force(temp_folder):
    os.makedirs(os.path.join(temp_folder.path, '.git'))
    subdir = os.path.join(temp_folder.path, 'a/b')
    os.makedirs(subdir)
    with pytest.raises(ValueError):
        Space.init(subdir)

def test_init_below_git_repo_root_succeeds_with_force(temp_folder):
    os.makedirs(os.path.join(temp_folder.path, '.git'))
    subdir = os.path.join(temp_folder.path, 'a/b')
    os.makedirs(subdir)
    Space.init(subdir, force=True)
    for item in ITEMS_CREATED_DURING_INIT:
        assert os.path.exists(os.path.join(subdir, item))

