# -*- coding: utf-8 -*-

"""Unit testing module for tf2docs pre-commit hook."""

import os
import tempfile
from unittest import mock

import pytest

import tf2docs.invoke


def test_binary_found_on_path():
    """Verify _terraform_docs_binary returns the PATH binary when present."""
    with mock.patch("shutil.which", return_value="/usr/bin/terraform-docs"):
        result = tf2docs.invoke._terraform_docs_binary()
    assert result == "/usr/bin/terraform-docs"


def test_binary_cached_in_install_dir():
    """Verify cached binary is returned without downloading."""
    with tempfile.TemporaryDirectory() as tmpdir:
        install_dir = os.path.join(tmpdir, ".terraform-docs", "bin")
        os.makedirs(install_dir)
        cached = os.path.join(install_dir, "terraform-docs")
        open(cached, "w").close()

        with mock.patch("shutil.which", return_value=None), mock.patch(
            "os.path.expanduser", return_value=tmpdir
        ), mock.patch("urllib.request.urlretrieve") as mock_dl:
            result = tf2docs.invoke._terraform_docs_binary()

        mock_dl.assert_not_called()
        assert result == cached


def test_binary_downloads_when_missing():
    """Verify _terraform_docs_binary downloads and extracts the binary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        install_dir = os.path.join(tmpdir, ".terraform-docs", "bin")
        binary_path = os.path.join(install_dir, "terraform-docs")

        mock_member = mock.Mock()
        mock_member.name = "terraform-docs"
        mock_tar = mock.MagicMock()
        mock_tar.__enter__ = mock.Mock(return_value=mock_tar)
        mock_tar.__exit__ = mock.Mock(return_value=False)
        mock_tar.getmember.return_value = mock_member
        mock_tar.extract.side_effect = lambda m, path: (
            os.makedirs(path, exist_ok=True)
            or open(os.path.join(path, "terraform-docs"), "w").close()
        )

        with mock.patch("shutil.which", return_value=None), mock.patch(
            "os.path.expanduser", return_value=tmpdir
        ), mock.patch("urllib.request.urlretrieve"), mock.patch(
            "tarfile.open", return_value=mock_tar
        ), mock.patch(
            "os.chmod"
        ):
            result = tf2docs.invoke._terraform_docs_binary(version="v0.22.0")

        assert result == binary_path


def test_binary_uses_custom_version():
    """Verify custom version is used in the download URL."""
    with tempfile.TemporaryDirectory() as tmpdir:
        captured_urls = []

        def fake_retrieve(url, path):
            captured_urls.append(url)

        mock_member = mock.Mock()
        mock_member.name = "terraform-docs"
        mock_tar = mock.MagicMock()
        mock_tar.__enter__ = mock.Mock(return_value=mock_tar)
        mock_tar.__exit__ = mock.Mock(return_value=False)
        mock_tar.getmember.return_value = mock_member
        mock_tar.extract.side_effect = lambda m, path: (
            os.makedirs(path, exist_ok=True)
            or open(os.path.join(path, "terraform-docs"), "w").close()
        )

        with mock.patch("shutil.which", return_value=None), mock.patch(
            "os.path.expanduser", return_value=tmpdir
        ), mock.patch(
            "urllib.request.urlretrieve", side_effect=fake_retrieve
        ), mock.patch(
            "tarfile.open", return_value=mock_tar
        ), mock.patch(
            "os.chmod"
        ):
            tf2docs.invoke._terraform_docs_binary(version="v0.19.0")

        assert len(captured_urls) == 1
        assert "v0.19.0" in captured_urls[0]


def test_main_with_version_arg():
    """Verify --terraform-docs-version arg is passed through to run()."""
    with mock.patch("tf2docs.invoke.run", return_value=0) as mock_run:
        tf2docs.invoke.main(["--terraform-docs-version", "v0.19.0"])
    mock_run.assert_called_once_with([], version="v0.19.0")


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
    """Verify directory without README.md is skipped silently."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a terraform file in a subdirectory
        test_dir = os.path.join(tmpdir, "terraform")
        os.makedirs(test_dir)
        test_file = os.path.join(test_dir, "main.tf")

        with open(test_file, "w") as f:
            f.write("# terraform file")

        return_code = tf2docs.invoke.run([test_file])
        assert return_code == 0


def test_run_missing_markers():
    """Verify README.md without markers is skipped silently."""
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
        assert return_code == 0


def test_run_terraform_docs_not_found():
    """Verify error when terraform-docs cannot be found or installed."""
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

        with mock.patch(
            "tf2docs.invoke._terraform_docs_binary"
        ) as mock_binary:
            mock_binary.side_effect = Exception("terraform-docs not found")
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

        assert (
            return_code == 1
        )  # non-zero signals pre-commit that files changed

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
            "<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
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


def test_run_no_filenames():
    """Verify hook exits early when no filenames are provided."""
    return_code = tf2docs.invoke.run([])
    assert return_code == 0


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

        assert (
            return_code == 1
        )  # non-zero signals pre-commit that files changed
