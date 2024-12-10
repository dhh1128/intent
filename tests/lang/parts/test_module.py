from .util import DATA_DIR, SPACE1_DIR, temp_folder
from intent.lang.parts import Module, Space

space1 = Space(SPACE1_DIR)

def test_single_file():
    path = SPACE1_DIR + "/pickle.i"
    m = Module(path, space1)
    assert m.name == 'pickle'
    assert m.sid == '/pickle'

def test_3_part_module_from_pre():
    path = SPACE1_DIR + "/orchard/apple.i"
    m = Module(path, space1)
    assert m.name == 'apple'
    assert m.sid == '/orchard/apple'

