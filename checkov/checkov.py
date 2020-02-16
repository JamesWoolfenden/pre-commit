"""Checkov"""
from __future__ import print_function
import argparse
import subprocess
import sys
import os.path


def run(dir):
    """Run 'checkov' command on a dir."""
    subprocess.run(["checkov","-d", dir])    
    return
    
def main(argv=None):
    """Main execution path."""

    #print(os.path.dirname("/mnt/c/code/travst.txt"))
    print(argv)
    parser = argparse.ArgumentParser()
    
    parser.add_argument('--dir', help='path to analyse')
    
    args = parser.parse_args(argv)

    return run(args.dir)



if __name__ == "__main__":
    exit(main())
