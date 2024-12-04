import os
import pytest
import shutil
import tempfile

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data'))
SPACE1_DIR = os.path.join(DATA_DIR, 'space1')

class TempFolder:
    def __init__(self) -> None:
        self._path: str = None

    @property
    def path(self):
        if self._path is None:
            self._path = tempfile.mkdtemp()
        return self._path

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.path)

@pytest.fixture
def temp_folder():
    # In order to guarantee that the folder is deleted after
    # the test, we need to use a with statement to enter and
    # exit the context manager. Turn this fixture into a
    # generator so we can yield inside the with.
    with TempFolder() as tf:
        yield tf

