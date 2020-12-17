#!/usr/bin/env python3
"""
This module provides an interface for getting any directory that is used
throughout the project.  This gives a centralized place to update if the
project installation structure changes.

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import os.path



def get_root_path():
    """
    Get the root path to the project/repo root dir.

    Returns:
      (os.path): Path to root dir.
    """
    repo_root_dir = os.path.dirname(get_src_app_root_path())
    return repo_root_dir



def get_src_app_root_path():
    """
    Get the path to project/app source root dir.

    Returns:
      (os.path): Path to source root dir.
    """
    this_script_dir = os.path.dirname(os.path.realpath(__file__))
    main_script_dir = os.path.dirname(this_script_dir)
    return main_script_dir



def get_conf_path():
    """
    Get the path to configuration files.

    Returns:
      (os.path): Path to config dir.
    """
    return os.path.join(get_root_path(), 'config')
