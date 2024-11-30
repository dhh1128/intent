from setuptools import setup, find_packages

setup(
    name="intent",  # Package name for PyPI
    version="0.1.0",  # Version of the package
    packages=find_packages(),
    install_requires=[
        'ruamel.yaml~=0.18.6',
        'ruamel.yaml.clib~=0.2.12',
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
