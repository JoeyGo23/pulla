#!/usr/bin/env python3

from __future__ import print_function

import sys
import os
import argparse

from .pulla import Pulla
from .utils import is_this_a_git_dir

def main():
    ''' Main
    '''
    # Parse command line arguments
    #usage = "%prog [-f credential_file]"
    #parser = ArgumentParser(usage=usage)
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--folder', type=str, dest='folder',
                        help='Update the repos in this folder')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Show verbose information. Higher verbosity can be selected by --verbosity flag')

    #parser.add_argument('otherthings', nargs='*')
    #args = parser.parse_args()
    args, otherthings = parser.parse_known_args()
    argc = len(otherthings)


    directory = os.path.abspath(os.curdir)
    if args.folder:
        directory = args.folder

    verbosity = None
    if args.verbose:
        verbosity = 1

    pulla = Pulla(verbosity=verbosity, recursive=False)

    if is_this_a_git_dir(directory):
        pulla.do_pull_in(directory)
    else:
        pulla.pull_all(directory)

if __name__ == '__main__':
    sys.exit(main())
