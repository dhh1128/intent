import os
import pytest

from .util import DATA_DIR
IIGNORE_DIR = os.path.join(DATA_DIR, 'iignore')
IIGNORE_NOIGNORES_DIR = os.path.join(IIGNORE_DIR, 'noignores')
IIGNORE_SOMEIGNORES_DIR = os.path.join(IIGNORE_DIR, 'someignores')

from intent.lang.parts import Space, HierarchicalDotIIgnore

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
