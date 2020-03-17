#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import os
from setuptools import setup, find_packages


def local_file(*f):
    with open(os.path.join(os.path.dirname(__file__), *f), "r") as fd:
        return fd.read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = "version"

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except Exception:
            self.version = None


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file("uiclasses", "version.py")))
    return finder.version


setup(
    name="uiclasses",
    version=read_version(),
    description="\n".join(["Data-Modeling for User Interfaces"]),
    long_description=local_file("README.rst"),
    entry_points={"console_scripts": ["uiclasses = uiclasses.cli:entrypoint"]},
    url="https://github.com/NewStore-oss/uiclasses",
    project_urls={
        "Documentation": "https://uiclasses.readthedocs.io/en/latest/",
        "Source Code": "https://github.com/NewStore-oss/uiclasses",
        "Issue Tracker": "https://github.com/NewStore-oss/uiclasses/issues",
        "Test Coverage": "https://codecov.io/gh/NewStore-oss/uiclasses",
    },
    packages=find_packages(exclude=["*tests*"]),
    include_package_data=True,
    package_data={"uiclasses": ["README.rst", "*.png", "*.rst", "docs/*", "docs/*/*"]},
    package_dir={"uiclasses": "uiclasses"},
    zip_safe=False,
    author="NewStore GmbH",
    author_email="opensource+pypi@newstore.com",
    maintainer="Gabriel Falcão",
    maintainer_email="gabriel@nacaolivre.org",
    python_requires=">=3.6",
    install_requires=local_file("requirements.txt").splitlines(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Environment :: MacOS X",
        "Environment :: Handhelds/PDA's",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    dependency_links=[],
)
