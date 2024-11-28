from setuptools import setup, find_packages

setup(
    name="intent",  # Package name for PyPI
    version="0.1.0",  # Version of the package
    packages=find_packages(),
    install_requires=[],
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
