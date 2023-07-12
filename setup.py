#!/usr/bin/env python3

import os
from setuptools import setup

# get key package details from sm_particle_counter/__version__.py
about = {}  # type: ignore
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "sm_particle_counter", "__version__.py")) as f:
    exec(f.read(), about)

# load the README file and use it as the long_description for PyPI
with open("README.md", "r") as f:
    readme = f.read()

# package configuration - for reference see:
# https://setuptools.readthedocs.io/en/latest/setuptools.html#id9
setup(
    name=about["__title__"],
    description=about["__description__"],
    long_description=readme,
    long_description_content_type="text/markdown",
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    url=about["__url__"],
    packages=["sm_particle_counter"],
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "numpy",
        "pandas",
        "dask_image",
        "dask[distributed]",
        "scipy",
        "bokeh",
        "matplotlib",
        "pytest",
        "PIL",
        "pims",
        "docopt"
    ],
    license=about["__license__"],
    zip_safe=False,
    entry_points={
        "console_scripts": ["sm_particle_counter=sm_particle_counter.main:particle_count_main",
                            "estimate_rise_time=sm_particle_counter.main:rise_time_main",
                            "tirf_intensity=sm_particle_counter.tirf_intensity:main"],
    },
    classifiers=[
        "Programming Language :: Python :: 3.9",
    ],
)
