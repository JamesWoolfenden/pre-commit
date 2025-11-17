# -*- coding: utf-8 -*-

"""Unit testing module for checkov pre-commit hook."""

import os
from unittest import mock

import checkov.invoke


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def test_checkov_no_files():
    """Verify that running with no files returns an error."""
    return_code = checkov.invoke.run([])
    assert return_code == 1


def test_checkov_with_valid_files():
    """Verify that running with valid terraform files works."""
    test_files = [
        os.path.join(DATA_DIR, "ok", "formatted", "ok_terraform_1.tf"),
        os.path.join(DATA_DIR, "ok", "formatted", "ok_terraform_2.tf"),
    ]

    # Mock subprocess.run to avoid actually running checkov
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0)
        return_code = checkov.invoke.run(test_files)

        # Verify checkov was called with the correct directory
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert call_args[0][0][0] == "checkov"
        assert call_args[0][0][1] == "-d"
        # Should call on the parent directory
        assert "ok/formatted" in call_args[0][0][2]

    assert return_code == 0


def test_checkov_windows_command():
    """Verify that Windows uses checkov.cmd."""
    test_files = [
        os.path.join(DATA_DIR, "ok", "formatted", "ok_terraform_1.tf")
    ]

    with mock.patch("os.name", "nt"):
        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock.Mock(returncode=0)
            checkov.invoke.run(test_files)

            call_args = mock_run.call_args
            assert call_args[0][0][0] == "checkov.cmd"


def test_checkov_not_installed():
    """Verify proper error handling when checkov is not installed."""
    test_files = [
        os.path.join(DATA_DIR, "ok", "formatted", "ok_terraform_1.tf")
    ]

    with mock.patch("subprocess.run") as mock_run:
        mock_run.side_effect = FileNotFoundError("checkov not found")
        return_code = checkov.invoke.run(test_files)

    assert return_code == 1


def test_checkov_failure():
    """Verify that checkov failures are properly propagated."""
    test_files = [
        os.path.join(DATA_DIR, "ok", "formatted", "ok_terraform_1.tf")
    ]

    with mock.patch("subprocess.run") as mock_run:
        # Checkov returns non-zero when it finds issues
        mock_run.return_value = mock.Mock(returncode=1)
        return_code = checkov.invoke.run(test_files)

    # The return code should match checkov's return code
    assert return_code == 1


def test_checkov_main():
    """Test the main entry point."""
    with mock.patch("subprocess.run") as mock_run:
        mock_run.return_value = mock.Mock(returncode=0)
        return_code = checkov.invoke.main(
            [os.path.join(DATA_DIR, "ok", "formatted", "ok_terraform_1.tf")]
        )

    assert return_code == 0
