#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""setup.py - Generic setup script."""


import setuptools


setuptools.setup(
    name="pre-commit-terraform-fmt",
    description="Rewrite Terraform configuration files to a canonical format"
    "and style",
    url="https://github.com/melmorabity/pre-commit-terraform-fmt",
    version="0.0.1",
    author="Mohamed El Morabity",
    author_email="melmorabity@fedoraproject.org",
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=setuptools.find_packages(exclude="tests"),
    setup_requires=["pytest-runner"],
    install_requires=['future;python_version<"3.0"'],
    tests_require=["pytest", "pytest-datafiles", "pytest-pylint"],
    entry_points={"console_scripts": ["terraform-fmt = terraform.fmt:main",
	"checkov = checkov.invoke:main"]},
)
