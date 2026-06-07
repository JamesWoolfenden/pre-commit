# -*- coding: utf-8 -*-
"""terraform-docs"""

import argparse
import hashlib
import os.path
import platform
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import zipfile

readmefile = "README.md"

TERRAFORM_DOCS_VERSION = "v0.23.0"

# From terraform-docs-v0.23.0.sha256sum — release assets are mutable, so verify.
# fmt: off
TERRAFORM_DOCS_SHA256 = {
    ("darwin", "amd64"): "b47e2087d558df3bd79b7ae67983b310d2e3db8c7b6dcd543249a757b48ed4c3",  # noqa: E501
    ("darwin", "arm64"): "2a91629a37392f545a96c63d69e2c98822cd69f284e81e7dab2e30b15d2911a4",  # noqa: E501
    ("linux", "amd64"): "80b8cd1d08b44e1182a39177adafc6901650a22e0a7f52cfeffcdbd44e8b0938",  # noqa: E501
    ("linux", "arm64"): "f3be6f09fb0913c752b78480fac1eb4916e9ee50da7e3eb0bdaa356d80ed16b5",  # noqa: E501
    ("windows", "amd64"): "f789b747da9e373012f2e3ceeb7802572f1893adad3c97bd66bc5dfa34b341b1",  # noqa: E501
    ("windows", "arm64"): "d29faa8629f22eeb6718a78302ebca115f73532986a2a71280321d3f49327cff",  # noqa: E501
}
# fmt: on


def _terraform_docs_binary(version=TERRAFORM_DOCS_VERSION):
    """Return path to terraform-docs, downloading it if not on PATH."""
    binary = shutil.which("terraform-docs")
    if binary:
        return binary

    system = platform.system().lower()
    arch = platform.machine().lower()
    if arch in ("x86_64", "amd64"):
        arch = "amd64"
    elif arch in ("arm64", "aarch64"):
        arch = "arm64"
    exe = ".exe" if system == "windows" else ""

    install_dir = os.path.join(
        os.path.expanduser("~"), ".terraform-docs", "bin"
    )
    binary_path = os.path.join(install_dir, "terraform-docs" + exe)
    if os.path.isfile(binary_path):
        return binary_path

    want = TERRAFORM_DOCS_SHA256.get((system, arch))
    if version != TERRAFORM_DOCS_VERSION or want is None:
        raise RuntimeError(
            f"no pinned checksum for terraform-docs {version} {system}/{arch};"
            " install terraform-docs on PATH yourself"
        )

    os.makedirs(install_dir, exist_ok=True)
    ext = "zip" if system == "windows" else "tar.gz"
    filename = f"terraform-docs-{version}-{system}-{arch}.{ext}"
    url = (
        f"https://github.com/terraform-docs/terraform-docs/releases/download"
        f"/{version}/{filename}"
    )
    print(f"Downloading terraform-docs {version}...", file=sys.stderr)
    with tempfile.TemporaryDirectory() as tmpdir:
        archive = os.path.join(tmpdir, filename)
        urllib.request.urlretrieve(url, archive)
        with open(archive, "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        if got != want:
            raise RuntimeError(
                f"terraform-docs checksum mismatch for {filename}: "
                f"expected {want}, got {got}"
            )
        staged = f"{binary_path}.{os.getpid()}.tmp"
        if system == "windows":
            with zipfile.ZipFile(archive) as zf:
                with zf.open("terraform-docs.exe") as src, open(
                    staged, "wb"
                ) as dst:
                    shutil.copyfileobj(src, dst)
        else:
            with tarfile.open(archive) as tar:
                with tar.extractfile("terraform-docs") as src, open(
                    staged, "wb"
                ) as dst:
                    shutil.copyfileobj(src, dst)
            os.chmod(staged, 0o755)
    try:
        os.replace(staged, binary_path)
    except OSError:
        os.remove(staged)
        if not os.path.isfile(binary_path):
            raise
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


def run(filenames, version=TERRAFORM_DOCS_VERSION):
    """Run terraform-docs and update README.md with generated documentation."""
    if not filenames:
        return 0

    try:
        binary = _terraform_docs_binary(version=version)
    except Exception as e:
        print(f"Error installing terraform-docs: {e}", file=sys.stderr)
        return 1

    reg = re.compile(
        "(?<=<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->)"
        "(.*?)"
        "(?=<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->)",
        re.DOTALL,
    )

    # Collect unique directories, preserving shortest-first order so a repo
    # root is processed before its subdirectories.
    seen = set()
    folders = []
    for f in filenames:
        d = os.path.abspath(os.path.dirname(f))
        if d not in seen:
            seen.add(d)
            folders.append(d)
    folders.sort(key=len)

    ret = 0
    for folder in folders:
        readmepath = os.path.join(folder, readmefile)
        try:
            oldblock = readme(readmepath)
        except FileNotFoundError:
            continue  # no README in this directory — skip silently
        except IOError as e:
            print(f"Error: {e}", file=sys.stderr)
            ret = 1
            continue

        if (
            "<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->"
            not in oldblock
            or "<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->" not in oldblock
        ):
            continue  # markers absent — not our README to manage

        paramblock = subprocess.run(
            [binary, "md", "--lockfile=false", os.path.join(folder, "")],
            shell=False,
            text=True,
            capture_output=True,
            encoding="utf-8",
            check=False,
        )

        if paramblock.returncode != 0:
            print(
                f"Error running terraform-docs: {paramblock.stderr}",
                file=sys.stderr,
            )
            ret = paramblock.returncode
            continue

        nublock = reg.sub("\n" + paramblock.stdout, oldblock)
        if nublock == oldblock:
            continue

        try:
            writeme(readmepath, nublock)
            print(f"Updated {readmepath}")
            ret = 1  # signal pre-commit that files were modified
        except IOError as e:
            print(f"Error: {e}", file=sys.stderr)
            ret = 1

    return ret


def main(argv=None):
    """Main execution path."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )
    parser.add_argument(
        "--terraform-docs-version",
        default=TERRAFORM_DOCS_VERSION,
        help="terraform-docs version to download if not on PATH"
        " (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    return run(args.filenames, version=args.terraform_docs_version)


if __name__ == "__main__":
    exit(main())
