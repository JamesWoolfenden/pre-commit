"""Checkov"""
from __future__ import print_function
import argparse
import subprocess
import sys
import os.path


def run(filenames):
    """Run 'checkov' command on a dir."""
    
    folders=[]
    for file in filenames:
        folders.append(os.path.dirname(file))
    
    # get root
    root=os.path.abspath(min(set(folders), key=len))

    subprocess.check_output(["checkov","-d", os.path.join(root, '')])    
    return
    
def main(argv=None):
    """Main execution path."""

    print(argv)
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.")
    
    args = parser.parse_args(argv)

    return run(args.filenames)



if __name__ == "__main__":
    exit(main())
