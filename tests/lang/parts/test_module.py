from .util import DATA_DIR, SPACE1_DIR, temp_folder
from intent.lang.parts import Module, Space

space1 = Space(SPACE1_DIR)

def test_single_file():
    path = SPACE1_DIR + "/pickle.i"
    m = Module(path, space1)
    assert m.rel_path == '/pickle.i'
