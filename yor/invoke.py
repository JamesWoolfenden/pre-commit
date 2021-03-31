# -*- coding: utf-8 -*-
"""yor"""

import argparse
import subprocess
import sys
import os.path


def run():
    folder="example/examplea"
    """Run 'yor' command on a dir."""
    stdout = subprocess.run(
        ["yor", "tag -d", folder], shell=False, capture_output=False)

    if stdout:
        print("Analysed {}".format(folder), file=sys.stderr)
    return stdout.returncode


def main(argv=None):
    """Main execution path."""

    return run()


if __name__ == "__main__":
    exit(main())
