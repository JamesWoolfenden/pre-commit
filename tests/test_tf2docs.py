# -*- coding: utf-8 -*-

"""Unit testing module for tf2docs pre-commit hook."""

import os
import tempfile
from unittest import mock

import pytest

import tf2docs.invoke


def test_readme_file_not_found():
    """Verify proper error when README file doesn't exist."""
    with pytest.raises(FileNotFoundError) as exc_info:
        tf2docs.invoke.readme("/nonexistent/path/README.md")
    assert "README file not found" in str(exc_info.value)


def test_readme_success():
    """Verify successful README reading."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        f.write("# Test README\nSome content")
        temp_path = f.name

    try:
        content = tf2docs.invoke.readme(temp_path)
        assert content == "# Test README\nSome content"
    finally:
        os.unlink(temp_path)


def test_writeme_success():
    """Verify successful README writing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False, encoding="utf-8"
    ) as f:
        temp_path = f.name

    try:
        result = tf2docs.invoke.writeme(temp_path, "Updated content")
        assert result == 0

        with open(temp_path, "r", encoding="utf-8") as f:
            content = f.read()
        assert content == "Updated content"
    finally:
        os.unlink(temp_path)


def test_run_missing_readme():
    """Verify error when README.md is missing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a terraform file in a subdirectory
        test_dir = os.path.join(tmpdir, "terraform")
        os.makedirs(test_dir)
        test_file = os.path.join(test_dir, "main.tf")

        with open(test_file, "w") as f:
            f.write("# terraform file")

        return_code = tf2docs.invoke.run([test_file])
        assert return_code == 1


def test_run_missing_markers():
    """Verify error when README.md is missing required comment markers."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a terraform file
        test_file = os.path.join(tmpdir, "main.tf")
        with open(test_file, "w") as f:
            f.write("# terraform file")

        # Create a README without markers
        readme_path = os.path.join(tmpdir, "README.md")
        with open(readme_path, "w") as f:
            f.write("# My Terraform Module\n\nNo markers here!")

        return_code = tf2docs.invoke.run([test_file])
        assert return_code == 1


def test_run_terraform_docs_not_found():
    """Verify error when terraform-docs is not installed."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a terraform file
        test_file = os.path.join(tmpdir, "main.tf")
        with open(test_file, "w") as f:
            f.write("# terraform file")

        # Create a README with markers
        readme_path = os.path.join(tmpdir, "README.md")
        with open(readme_path, "w") as f:
            f.write(
                "# My Module\n"
                "<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
                "<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
            )

        # Mock subprocess to raise FileNotFoundError
        with mock.patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError(
                "terraform-docs not found"
            )
            return_code = tf2docs.invoke.run([test_file])

        assert return_code == 1


def test_run_success_with_update():
    """Verify successful documentation update."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a terraform file
        test_file = os.path.join(tmpdir, "main.tf")
        with open(test_file, "w") as f:
            f.write(
                'variable "example" {\n'
                '  description = "An example variable"\n'
                "  type = string\n"
                "}\n"
            )

        # Create a README with markers
        readme_path = os.path.join(tmpdir, "README.md")
        original_content = (
            "# My Module\n"
            "<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
            "Old docs here\n"
            "<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
        )
        with open(readme_path, "w") as f:
            f.write(original_content)

        # Mock subprocess to return terraform-docs output
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = "## Inputs\n\n| Name | Description |\n"

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_result
            return_code = tf2docs.invoke.run([test_file])

        assert return_code == 0

        # Verify the README was updated
        with open(readme_path, "r") as f:
            updated_content = f.read()

        assert "## Inputs" in updated_content
        assert "Old docs here" not in updated_content


def test_run_no_update_needed():
    """Verify no update when docs are already current."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a terraform file
        test_file = os.path.join(tmpdir, "main.tf")
        with open(test_file, "w") as f:
            f.write("# terraform file")

        # Create a README with markers and existing docs
        readme_path = os.path.join(tmpdir, "README.md")
        docs_content = "## Inputs\n\n| Name | Description |\n"
        original_content = (
            "# My Module\n"
            "<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\r\n"
            + docs_content
            + "<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
        )
        with open(readme_path, "w") as f:
            f.write(original_content)

        # Mock subprocess to return same terraform-docs output
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = docs_content

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_result
            return_code = tf2docs.invoke.run([test_file])

        # Should return 0 when no update needed
        assert return_code == 0


def test_run_terraform_docs_failure():
    """Verify error handling when terraform-docs fails."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a terraform file
        test_file = os.path.join(tmpdir, "main.tf")
        with open(test_file, "w") as f:
            f.write("# terraform file")

        # Create a README with markers
        readme_path = os.path.join(tmpdir, "README.md")
        with open(readme_path, "w") as f:
            f.write(
                "# My Module\n"
                "<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
                "<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
            )

        # Mock subprocess to return error
        mock_result = mock.Mock()
        mock_result.returncode = 1
        mock_result.stderr = "Error parsing terraform files"

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_result
            return_code = tf2docs.invoke.run([test_file])

        assert return_code == 1


def test_main():
    """Test the main entry point."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a terraform file
        test_file = os.path.join(tmpdir, "main.tf")
        with open(test_file, "w") as f:
            f.write("# terraform file")

        # Create a README with markers
        readme_path = os.path.join(tmpdir, "README.md")
        with open(readme_path, "w") as f:
            f.write(
                "# My Module\n"
                "<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
                "<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
            )

        # Mock subprocess
        mock_result = mock.Mock()
        mock_result.returncode = 0
        mock_result.stdout = "## Docs\n"

        with mock.patch("subprocess.run") as mock_run:
            mock_run.return_value = mock_result
            return_code = tf2docs.invoke.main([test_file])

        assert return_code == 0
