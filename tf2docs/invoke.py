# -*- coding: utf-8 -*-
"""terraform-docs"""

import argparse
import subprocess
import os.path
import re
import sys

readmefile = "README.md"


def readme(readmefile):
    """Read README file and return contents."""
    try:
        with open(readmefile, "r", encoding="utf-8", newline="\n") as f:
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
    myrootfolder = None
    folders = []
    for files in filenames:
        folders.append(os.path.dirname(files))

    myrootfolder = os.path.join(
        os.path.abspath(min(folders, key=len, default=".")), ""
    )

    readmepath = os.path.join(myrootfolder, readmefile)

    try:
        oldblock = readme(readmepath)
    except (FileNotFoundError, IOError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    # Check for required comment markers
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
        paramblock = subprocess.run(
            ["terraform-docs", "md", myrootfolder],
            shell=False,
            text=True,
            capture_output=True,
            encoding=None,
            check=False,
        )
    except FileNotFoundError:
        print(
            "Error: terraform-docs command not found.\n"
            "Please install terraform-docs: \n"
            "   https://github.com/terraform-docs/terraform-docs",
            file=sys.stderr,
        )
        return 1

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
