#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""setup.py - Generic setup script."""


import setuptools


setuptools.setup(
    name="pre-commit",
    description="Rewrite Terraform configuration files to a canonical format"
    "and style",
    url="https://github.com/jameswoolfenden/pre-commit",
    version="0.1.3",
    author=["Mohamed El Morabity", "James Woolfenden"],
    author_email="james.woolfenden@gmail.com",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=setuptools.find_packages(exclude="tests"),
    setup_requires=["pytest-runner"],
    install_requires=['future;python_version<"3.0"'],
    tests_require=["pytest", "pytest-datafiles", "pytest-pylint"],
    entry_points={
        "console_scripts": [
            "terraform-fmt = terraform.fmt:main",
            "checkov-scan = checkov.invoke:main",
            "yor = yor.invoke:main",
            "tf2docs = tf2docs.invoke:main",
        ]
    },
)
