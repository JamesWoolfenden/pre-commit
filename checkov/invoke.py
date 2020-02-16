# -*- coding: utf-8 -*-
"""Checkov"""
from __future__ 
import print_function
import argparse
import subprocess
import sys
import os.path


def run(filenames):
    """Run 'checkov' command on a dir."""
    invalid = False
    folders=[]
    for file in filenames:
        folders.append(os.path.dirname(file))
    
    # get root
    root=os.path.abspath(min(set(folders), key=len))
    print(root)
    
    stdout=subprocess.run(["checkov","-d", os.path.join(root, '')], shell=False, capture_output=False)    

    print(stdout)

    if stdout:
        invalid = True
        print("Analysed {}".format(root), file=sys.stderr)
    return int(invalid)
    
def main(argv=None):
    """Main execution path."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.")
    
    args = parser.parse_args(argv)

    return run(args.filenames)



if __name__ == "__main__":
    exit(main())
