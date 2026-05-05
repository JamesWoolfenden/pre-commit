# -*- coding: utf-8 -*-
"""terraform-docs"""

import argparse
import os.path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

readmefile = "README.md"

TERRAFORM_DOCS_VERSION = "v0.22.0"


def _terraform_docs_binary():
    """Return path to terraform-docs, downloading it if not on PATH."""
    binary = shutil.which("terraform-docs")
    if binary:
        return binary

    system = platform.system().lower()
    arch = platform.machine().lower()
    if arch == "x86_64":
        arch = "amd64"
    elif arch in ("arm64", "aarch64"):
        arch = "arm64"

    install_dir = os.path.join(
        os.path.expanduser("~"), ".terraform-docs", "bin"
    )
    binary_path = os.path.join(install_dir, "terraform-docs")
    if os.path.isfile(binary_path):
        return binary_path

    os.makedirs(install_dir, exist_ok=True)
    filename = (
        f"terraform-docs-{TERRAFORM_DOCS_VERSION}-{system}-{arch}.tar.gz"
    )
    url = (
        f"https://github.com/terraform-docs/terraform-docs/releases/download"
        f"/{TERRAFORM_DOCS_VERSION}/{filename}"
    )
    print(
        f"Downloading terraform-docs {TERRAFORM_DOCS_VERSION}...",
        file=sys.stderr,
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        archive = os.path.join(tmpdir, filename)
        urllib.request.urlretrieve(url, archive)
        with tarfile.open(archive) as tar:
            member = tar.getmember("terraform-docs")
            member.name = "terraform-docs"
            tar.extract(member, path=install_dir)
    os.chmod(binary_path, 0o755)
    return binary_path


def readme(readmefile):
    """Read README file and return contents."""
    try:
        with open(readmefile, "r", encoding="utf-8", newline=None) as f:
            contents = f.read()
        return contents
    except FileNotFoundError:
        raise FileNotFoundError(
            f"README file not found: {readmefile}. "
            "Ensure README.md exists in the Terraform module directory."
        )
    except IOError as e:
        raise IOError(f"Error reading {readmefile}: {e}")


def writeme(readmefile, block):
    """Write updated content to README file."""
    try:
        with open(readmefile, "w", encoding="utf-8", newline="\n") as f:
            f.write(block)
        return 0
    except IOError as e:
        raise IOError(f"Error writing to {readmefile}: {e}")


def run(filenames):
    """Run terraform-docs and update README.md with generated documentation."""
    if not filenames:
        return 0

    folders = [os.path.dirname(f) for f in filenames]
    myrootfolder = os.path.join(os.path.abspath(min(folders, key=len)), "")
    readmepath = os.path.join(myrootfolder, readmefile)

    try:
        oldblock = readme(readmepath)
    except (FileNotFoundError, IOError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if (
        "<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->" not in oldblock
        or "<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->" not in oldblock
    ):
        print(
            f"Error: {readmepath} is missing required comment markers.\n"
            "Please add the following to your README.md:\n"
            "<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->\n"
            "<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->",
            file=sys.stderr,
        )
        return 1

    try:
        binary = _terraform_docs_binary()
    except Exception as e:
        print(f"Error installing terraform-docs: {e}", file=sys.stderr)
        return 1

    paramblock = subprocess.run(
        [binary, "md", myrootfolder],
        shell=False,
        text=True,
        capture_output=True,
        encoding=None,
        check=False,
    )

    if paramblock.returncode != 0:
        print(
            f"Error running terraform-docs: {paramblock.stderr}",
            file=sys.stderr,
        )
        return paramblock.returncode

    reg = re.compile(
        "(?<=<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->)"
        "(.*?)"
        "(?=<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->)",
        re.DOTALL,
    )

    nublock = reg.sub("\r\n" + paramblock.stdout, oldblock)
    if nublock == oldblock:
        print("No update")
        return 0

    try:
        writeme(readmepath, nublock)
    except IOError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Updated {readmepath}")
    return 0


def main(argv=None):
    """Main execution path."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )
    args = parser.parse_args(argv)
    return run(args.filenames)


if __name__ == "__main__":
    exit(main())
