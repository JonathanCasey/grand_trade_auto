#!/usr/bin/env python3
"""
Checks python directories to ensure nothing is missing, such as modules missing
from the listing in `__init__.py` files.

This uses python import, so this must be called from a proper python env where
the directories-under-test are accessible.  In other words, it is best to call
from project root as
`python3 .circleci/dir_init_checker.py grand_trade_auto tests`.

Entire file is excluded from unit testing / code cov; but is still linted.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import argparse
import importlib
import os
import os.path
import sys



def main():
    """
    Main entry that uses CLI args to step through dir tree, reporting any
    missing or incorrect `__init__.py` config, and exits with a non-zero return
    code at the end if any missing/incorrect found.
    """
    args = parse_args()

    any_missing = False
    for root_dir in args.dirs:
        dirs_missing_init, dirs_missing_modules = check_full_dir(root_dir)

        for dir_path in dirs_missing_init:
            any_missing = True
            print(f'Missing __init__.py file in dir "{dir_path}"')

        for dir_path in dirs_missing_modules:
            any_missing = True
            print('Incorrect module listing (add/remove) in __init__.py file in'
                    f' dir "{dir_path}"')

    if any_missing:
        print(f'Failure in dir(s) {", ".join(args.dirs)} -- see above.')
        sys.exit(1)
    else:
        print(f'Passed for dir(s) {", ".join(args.dirs)}!')



def parse_args():
    """
    Parses the CLI input args.  Must be called only when run as a module; it is
    invalid to call as an import.

    Use the `python3 dir_init_checker.py -h` option to see the supported
    arguments summary.
    """
    assert __name__ == '__main__'

    parser = argparse.ArgumentParser(description=
            'Checks dirs for proper __init__.py usage.')
    parser.add_argument('dirs',
            nargs='+',
            help='Root dirs to check their contents in depth.')
    return parser.parse_args()



def check_full_dir(dir_path, dirs_missing_init=None, dirs_missing_modules=None):
    """
    Checks the provided directory and all of its subdirectories for proper
    `__init__.py` contents.

    This is intended to be called recursively.  There is no loop protection, so
    this is only intended to be used where there are no symlinks that may result
    in an infinite dir traversal loop.

    Args:
      dir_path (path/str): The path to the directory to review, including its
        sub directories.  Should be a relative path based on python env.
      dirs_missing_init ([path/str] or None): The list of dirs identified as
        missing `__init__.py` files when there are other `.py` files.  It is
        common to omit on initial invocation.
      dirs_missing_modules ([path/str] or None): The list of dirs identified as
        having an `__init__.py` file, but it is missing at least 1 module or has
        at least 1 module that no longer exists.  It is common to omit on
        initial invocation.

    Returns:
      dirs_missing_init ([path/str]): The list of directories that are missing
        `__init__.py` files when there are `.py` files present.  This includes
        results from all subdirectories.  All dirs are relative path.
      dirs_missing_modules ([path/str]): THe list of directories that have an
        `__init__.py` file, but it is missing at least 1 module or has at least
        1 module that no longer exists.  This includes results from all
        subdirectories.  All dirs are relative path.
    """
    if dirs_missing_init is None:
        dirs_missing_init = []
    if dirs_missing_modules is None:
        dirs_missing_modules = []

    subdir_paths = []
    py_filenames = []
    init_py_name = None

    for item_name in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item_name)
        if os.path.isdir(item_path):
            subdir_paths.append(item_path)
        elif os.path.isfile(item_path):
            if item_name == '__init__.py':
                init_py_name = convert_path_to_package(dir_path) + '.__init__'
            elif os.path.splitext(item_path)[-1].lower() == '.py':
                py_filenames.append(os.path.splitext(item_name)[0])

    if init_py_name is None and py_filenames:
        dirs_missing_init.append(dir_path)
    elif init_py_name:
        init_module = importlib.import_module(init_py_name)
        if not set(init_module.__all__) == set(py_filenames):
            dirs_missing_modules.append(dir_path)

    for subdir in subdir_paths:
        check_full_dir(subdir, dirs_missing_init, dirs_missing_modules)

    return dirs_missing_init, dirs_missing_modules



def convert_path_to_package(dir_path):
    """
    This converts a directory path to a package name (e.g. from a/b/c to a.b.c).

    Args:
      dir_path (path/str): The directory path to convert to a package name.
        This should be a relative directory, probably to the python env.

    Returns:
      (str): The equivalent package name from the provided dir path.
    """
    remaining_dir = dir_path
    pkg_reversed_list = []
    while True:
        remaining_dir, tail_dir = os.path.split(remaining_dir)

        if tail_dir:
            pkg_reversed_list.append(tail_dir)

        if not remaining_dir:
            break

    return '.'.join(reversed(pkg_reversed_list))



if __name__ == '__main__':
    main()
