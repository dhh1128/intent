from intent.version import __version__
import re

semver_pat = re.compile(r'^\d+\.\d+\.\d+$')

def test_version():
    assert semver_pat.match(__version__)
