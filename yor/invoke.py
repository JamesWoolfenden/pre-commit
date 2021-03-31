# -*- coding: utf-8 -*-
"""yor"""

import argparse
import subprocess
import sys
import os.path


def run(folder):
    """Run 'yor' command on a dir."""
    stdout = subprocess.run(
        ["yor", "tag -d", folder], shell=False, capture_output=False)

    if stdout:
        print("Analysed {}".format(folder), file=sys.stderr)
    return stdout.returncode


def main(argv=None):
    """Main execution path."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "folder",
        nargs="*",
        help="Folder to run the analysis over.",
    )

    parser.add_argument("-d", help="directory to run against")

    args = parser.parse_args(argv)

    return run(args.folder)


if __name__ == "__main__":
    exit(main())
