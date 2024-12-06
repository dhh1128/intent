from setuptools import setup, find_packages

from pathlib import Path
import re

# Read the version from the version.py file.
verpat = re.compile(r'^__version__[ \t]*=[ \t]*"(.*?)"', re.M)
version_file = Path(__file__).parent / "intent" / "version.py"
with open(version_file, "rt") as f:
    __version__ = verpat.search(f.read()).group(1)

setup(
    name="intent",  # Package name for PyPI
    version=__version__,
    packages=find_packages(),
    install_requires=[
        'pathspec~=0.12.1',
        'rich~=13.9.4',
        'rich-argparse~=1.6.0'
    ],
    entry_points={
        'console_scripts': [
            'i = scripts.i:main',  # Maps 'i' to 'scripts/i.py' (the binary)
        ],
    },
    tests_require=['pytest'],  # Specifies pytest for testing
    test_suite='tests',  # Default test folder
    include_package_data=True,  # Include files from MANIFEST.in
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
