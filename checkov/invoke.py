# -*- coding: utf-8 -*-
"""Checkov""" 

import argparse
import subprocess
import sys
import os.path


def run(filenames):
    """Run 'checkov' command on a dir."""
    invalid = False
    myrootfolder=""
    folders=[]
    for file in filenames:
        folders.append(os.path.dirname(file))
    
    # get root folder
    myrootfolder=os.path.abspath(min(set(folders), key=len))
    
    stdout=subprocess.run(["checkov","-d", os.path.join(myrootfolder, '')], shell=False, capture_output=False)    

    if stdout:
        invalid = True
        print("Analysed {}".format(myrootfolder), file=sys.stderr)
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
