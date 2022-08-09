# -*- coding: utf-8 -*-
"""pike"""

import argparse
import subprocess
import os.path
import re

readmefile = "README.md"


def readme(readmefile):
    f = open(readmefile, "r", encoding="utf-8", newline="\n")
    if f.mode == "r":
        contents = f.read()
    f.close
    return contents


def writeme(readmefile, block):
    f = open(readmefile, "w+", encoding="utf-8", newline="\n")
    f.write(block)
    f.close
    return 0


def run(filenames):
    myrootfolder = None
    folders = []
    for files in filenames:
        folders.append(os.path.dirname(files))

    myrootfolder = os.path.join(
        os.path.abspath(min(folders, key=len, default=".")), ""
    )

    readmepath = os.path.join(myrootfolder, readmefile)
    oldblock = readme(readmepath)

    paramblock = subprocess.run(
        ["pike", "-d", myrootfolder, "scan"],
        shell=False,
        text=True,
        capture_output=True,
        encoding=None,
    )

    reg = re.compile(
        "(?<=<!-- BEGINNING OF PRE-COMMIT-PIKE DOCS HOOK -->)"
        "(.*?)"
        "(?=<!-- END OF PRE-COMMIT-PIKE DOCS HOOK -->)",
        re.DOTALL,
    )

    nublock = reg.sub("\r\n" + paramblock.stdout, oldblock)
    if nublock == oldblock:
        print("No update")
        exit(0)

    writeme(readmefile, nublock)

    return paramblock.returncode


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
