# -*- coding: utf-8 -*-
"""Checkov"""

import argparse
import subprocess
import sys
import os.path


def run(filenames):
    """Run 'checkov' command on a dir."""
    if not filenames:
        print("Error: No files provided to scan", file=sys.stderr)
        return 1

    myrootfolder = ""
    folders = []
    for files in filenames:
        folder = os.path.dirname(files)
        if folder:
            folders.append(folder)

    if not folders:
        folders.append(".")

    myrootfolder = os.path.join(
        os.path.abspath(min(folders, key=len, default=".")), ""
    )

    if not os.path.isdir(myrootfolder):
        print(f"Error: Directory not found: {myrootfolder}", file=sys.stderr)
        return 1

    checkov_cmd = "checkov.cmd" if os.name == "nt" else "checkov"

    try:
        result = subprocess.run(
            [checkov_cmd, "-d", myrootfolder],
            shell=False,
            capture_output=False,
            check=False,
        )
    except FileNotFoundError:
        print(
            f"Error: {checkov_cmd} command not found.\n"
            "Please install checkov: pip install checkov\n"
            "Or ensure it is available in your PATH.",
            file=sys.stderr,
        )
        return 1
    except Exception as e:
        print(f"Error running checkov: {e}", file=sys.stderr)
        return 1

    print("Analysed {}".format(myrootfolder), file=sys.stderr)
    return result.returncode


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
