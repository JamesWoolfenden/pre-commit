# -*- coding: utf-8 -*-
"""Checkov"""

import argparse
import subprocess
import sys
import os.path


def run(filenames):
    """Run 'checkov' command on a dir."""
    myrootfolder = ""
    folders = []
    for files in filenames:
        folders.append(os.path.dirname(files))

    myrootfolder = os.path.join(
        os.path.abspath(min(folders, key=len, default=".")), ""
    )

    if os.name == "nt":
        stdout = subprocess.run(
            ["checkov-scan.bat", "-d", myrootfolder],
            shell=False,
            capture_output=False,
        )
    else:
        stdout = subprocess.run(
            ["checkov", "-d", myrootfolder], shell=False, capture_output=False
        )

    if stdout:
        print("Analysed {}".format(myrootfolder), file=sys.stderr)
    return stdout.returncode


def main(argv=None):
    """Main execution path."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )

    parser.add_argument("-d", help="directory to run against")

    args = parser.parse_args(argv)

    return run(args.filenames)


if __name__ == "__main__":
    exit(main())
