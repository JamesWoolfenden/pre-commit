# -*- coding: utf-8 -*-

"""Unit testing module for pre-commit-terraform-fmt."""


import os
import filecmp
import shutil

import pytest

import terraform.fmt

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


@pytest.fixture(scope="session")
def terraform_available():
    """Check if terraform or tofu binary is available."""
    return (
        shutil.which("tofu") is not None
        or shutil.which("terraform") is not None
    )


@pytest.mark.datafiles(os.path.join(DATA_DIR, "ok", "formatted"))
def test_terraform_fmt_formatted(datafiles, terraform_available):
    """Verify that valid and well-formatted Terraform files are successfully
    parsed and not modified."""
    if not terraform_available:
        pytest.skip("terraform binary not available")

    files = [str(f) for f in datafiles.iterdir()]
    return_code = terraform.fmt.run(files)
    assert return_code == 0

    # Ensure files haven't changed after formatting
    dircmp = filecmp.dircmp(
        os.path.join(DATA_DIR, "ok", "formatted"), str(datafiles)
    )
    assert not dircmp.diff_files
    assert dircmp.same_files


@pytest.mark.datafiles(os.path.join(DATA_DIR, "ok", "unformatted"))
def test_terraform_fmt_unformatted(datafiles, terraform_available):
    """Verify that valid and unformatted Terraform files are successfully
    parsed and modified."""
    if not terraform_available:
        pytest.skip("terraform binary not available")

    files = [str(f) for f in datafiles.iterdir()]
    return_code = terraform.fmt.run(files)
    assert return_code != 0

    # Ensure files have changed after formatting
    dircmp = filecmp.dircmp(
        os.path.join(DATA_DIR, "ok", "unformatted"), str(datafiles)
    )
    assert dircmp.diff_files
    assert not dircmp.same_files

    # Compare resulting files with expected results
    dircmp = filecmp.dircmp(
        os.path.join(DATA_DIR, "ok", "formatted"), str(datafiles)
    )
    assert not dircmp.diff_files
    assert dircmp.same_files


@pytest.mark.datafiles(os.path.join(DATA_DIR, "ko"))
def test_terraform_fmt_ko(datafiles, terraform_available):
    """Verify that invalid Terraform files are not modified."""
    if not terraform_available:
        pytest.skip("terraform binary not available")

    files = [str(f) for f in datafiles.iterdir()]
    return_code = terraform.fmt.run(files)
    assert return_code != 0

    # Ensure files haven't changed after formatting attempt
    dircmp = filecmp.dircmp(os.path.join(DATA_DIR, "ko"), str(datafiles))
    assert not dircmp.diff_files
    assert dircmp.same_files


@pytest.mark.datafiles(os.path.join(DATA_DIR, "ok"))
def test_terraform_no_bin(datafiles):
    """Checks invalid Terraform paths."""

    files = [str(f) for f in datafiles.rglob("*.tf")]

    # No such file
    return_code = terraform.fmt.run(files, terraform=str(datafiles))
    assert return_code != 0

    # Permission denied
    return_code = terraform.fmt.run(files, terraform="/dev/null")
    assert return_code != 0
