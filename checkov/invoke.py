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
    
    temporary=os.path.abspath(min(set(folders), key=len))
    print("Temporary",temporary)
    # get root folder
    myrootfolder=os.path.join(temporary, '')
    
    stdout=subprocess.run(["checkov","-d", myrootfolder], shell=False, capture_output=False)    

    if stdout:
        invalid = True
        #print("Analysed {}".format(myrootfolder), myrootfolder=sys.stderr)
    return int(invalid)
    
def main(argv=None):
    """Main execution path."""

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.")
    
    parser.add_argument(
        "-d", help="directory to run against"
    )

    args = parser.parse_args(argv)

    return run(args.filenames)



if __name__ == "__main__":
    exit(main())
