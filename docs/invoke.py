# -*- coding: utf-8 -*-
"""terraform-docs"""

# import argparse
import subprocess
import os.path
import re

readmefile = "README.md"


def readme(readmefile):
    f = open(readmefile, "r")
    if f.mode == "r":
        contents = f.read()
    return contents


def run(filenames):
    myrootfolder = None
    folders = []
    for files in filenames:
        folders.append(os.path.dirname(files))

    myrootfolder = os.path.join(
        os.path.abspath(min(folders, key=len, default=".")), ""
    )

    ss = readme(readmefile)

    block = subprocess.run(
        ["terraform-docs", "md", myrootfolder],
        shell=False,
        text=True,
        capture_output=True,
        encoding=None,
    )

    reg = re.compile(
        "(?<=<!-- BEGINNING OF PRE-COMMIT-TERRAFORM DOCS HOOK -->)(\r?\n)"
        "(.*?)"
        "(?=\r?\n<!-- END OF PRE-COMMIT-TERRAFORM DOCS HOOK -->)",
        re.DOTALL,
    )
    nublock = reg.sub(block.stdout, ss)
    f = open(readmefile, "w+")
    f.write(nublock)
    f.close

    return


def main(argv=None):
    """Main execution path."""

    # parser = argparse.ArgumentParser()

    # parser.add_argument(
    #    "filenames",
    #    nargs="*",
    #    help="Filenames pre-commit believes are changed.",
    # )

    # parser.add_argument("md", help="directory to run against")

    # args = parser.parse_args(argv)

    # return run(args.filenames)
    return run()


if __name__ == "__main__":
    exit(main())
