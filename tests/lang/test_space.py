import os
import pytest

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
SPACE1_DIR = os.path.join(DATA_DIR, 'space1')
IIGNORE_DIR = os.path.join(DATA_DIR, 'iignore')
IIGNORE_NOIGNORES_DIR = os.path.join(IIGNORE_DIR, 'noignores')
IIGNORE_SOMEIGNORES_DIR = os.path.join(IIGNORE_DIR, 'someignores')

from intent.lang.env import Space, HierarchicalDotIIgnore

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

@pytest.fixture
def iignore():
    return HierarchicalDotIIgnore(IIGNORE_DIR)

def test_iignore(iignore):
    n = len(IIGNORE_DIR)
    def collect(topdown):
        results = []
        for root, dirs, files in os.walk(IIGNORE_DIR, topdown=topdown):
            for item in dirs + files:
                path = os.path.join(root, item)
                results.append((path[n:], iignore.test_path(path)))
        return results
    def check(item, ignored):
        ok = True
        i = item.find('ignored')
        if i > -1:
            assert 'included' not in item[i:]
            if not ignored:
                print(f'For topdown={topdown}, {item} should be ignored.')
                ok = False
        else:
            if ignored:
                print(f'For topdown={topdown}, {item} should be ignored.')
        return ok
    ok = True
    for topdown in [True, False]:
        results = collect(topdown)
        for item, ignored in results:
            ok = check(item, ignored) and ok
    assert ok
