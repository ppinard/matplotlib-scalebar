#!/usr/bin/env python

# Standard library modules.
from pathlib import Path

# Third party modules.
from setuptools import setup, find_packages

# Local modules.
import versioneer

# Globals and constants variables.
BASEDIR = Path(__file__).parent.resolve()

# Get the long description from the relevant file
with open(BASEDIR.joinpath("README.md"), "r") as f:
    long_description = f.read()

setup(
    name="matplotlib-scalebar",
    version=versioneer.get_version(),
    description="Artist for matplotlib to display a scale bar",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Philippe Pinard",
    author_email="philippe.pinard@gmail.com",
    maintainer="Philippe Pinard",
    maintainer_email="philippe.pinard@gmail.com",
    url="https://github.com/ppinard/matplotlib-scalebar",
    license="BSD",
    keywords="matplotlib scale micron bar",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    packages=find_packages(),
    package_data={},
    python_requires='~=3.7',
    install_requires=["matplotlib"],
    zip_safe=True,
    cmdclass=versioneer.get_cmdclass(),
)
