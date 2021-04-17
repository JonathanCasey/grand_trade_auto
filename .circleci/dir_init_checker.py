#!/usr/bin/env python3
"""
Checks python directories to ensure nothing is missing, such as modules missing
from the listing in `__init__.py` files.

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
        root_dir_path = os.path.abspath(root_dir)
        dirs_missing_init, dirs_missing_modules = check_full_dir(root_dir_path)

        for dir_path in dirs_missing_init:
            any_missing = True
            rel_dir = os.path.join(root_dir,
                    os.path.relpath(dir_path, root_dir_path))
            print(f'Missing __init__.py file in dir "{rel_dir}"')

        for dir_path in dirs_missing_modules:
            any_missing = True
            rel_dir = os.path.join(root_dir,
                    os.path.relpath(dir_path, root_dir_path))
            print('Incorrect module listing (add/remove) in __init__.py file in'
                    f' dir "{rel_dir}"')

    if any_missing:
        sys.exit(1)



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
        sub directories.
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
        results from all subdirectories.
      dirs_missing_modules ([path/str]): THe list of directories that have an
        `__init__.py` file, but it is missing at least 1 module or has at least
        1 module that no longer exists.  This includes results from all
        subdirectories.
    """
    if dirs_missing_init is None:
        dirs_missing_init = []
    if dirs_missing_modules is None:
        dirs_missing_modules = []

    subdir_paths = []
    py_filenames = []
    init_py_path = None

    for item_name in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item_name)
        if os.path.isdir(item_path):
            subdir_paths.append(item_path)
        elif os.path.isfile(item_path):
            if item_name == '__init__.py':
                init_py_path = item_path
            elif os.path.splitext(item_path)[-1].lower() == '.py':
                py_filenames.append(os.path.splitext(item_name)[0])

    if init_py_path is None and py_filenames:
        dirs_missing_init.append(dir_path)
    elif init_py_path:
        init_module = importlib.import_module(init_py_path)
        if not set(init_module.__all__) == set(py_filenames):
            dirs_missing_modules.append(dir_path)

    for subdir in subdir_paths:
        check_full_dir(subdir, dirs_missing_init, dirs_missing_modules)

    return dirs_missing_init, dirs_missing_modules



if __name__ == '__main__':
    main()
