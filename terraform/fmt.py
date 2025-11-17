# -*- coding: utf-8 -*-

"""Rewrite Terraform configuration files to a canonical format and style."""


from __future__ import print_function
import argparse
import subprocess
import sys


def run(filenames, terraform=None):
    """Run 'terraform fmt' command on a set of files."""

    if not terraform:
        terraform = "terraform"

    invalid = False
    command = [
        terraform,
        "fmt",
        "-check=false",
        "-list=true",
        "-diff=false",
        "-write=true",
    ]

    # terraform 'fmt' command only takes one file at a time
    for path in filenames:
        try:
            stdout = subprocess.check_output(command + [path])
            if stdout:
                invalid = True
                print("reformatted {}".format(path), file=sys.stderr)
        except subprocess.CalledProcessError:
            invalid = True
        except (IOError, OSError) as ex:
            print(ex, file=sys.stderr)
            invalid = True
            break

    return int(invalid)


def main(argv=None):
    """Main execution path."""

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "filenames",
        nargs="*",
        help="Filenames pre-commit believes are changed.",
    )
    parser.add_argument(
        "--terraform", help="Path to the Terraform executable."
    )

    args = parser.parse_args(argv)
    return run(args.filenames, terraform=args.terraform)


if __name__ == "__main__":
    exit(main())
