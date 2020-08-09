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
with open(BASEDIR.joinpath("README.rst"), "r") as f:
    long_description = f.read()

setup(
    name="matplotlib-scalebar",
    version=versioneer.get_version(),
    description="Artist for matplotlib to display a scale bar",
    long_description=long_description,
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
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    packages=find_packages(),
    package_data={},
    install_requires=["matplotlib"],
    zip_safe=True,
    cmdclass=versioneer.get_cmdclass(),
)
