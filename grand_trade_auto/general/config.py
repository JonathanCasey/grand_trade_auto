#!/usr/bin/env python3
"""This module handles access to the configuration files.  The configuration
files--including the environment files--are accessed by the other python scripts
through this file.

This is setup such that other files need only call the `get()` functions, and
all the loading and caching will happen automatically internal to this file.

As of right now, this is hard-coded to access configuration files at a specific
name and path.

Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import configparser
import itertools
import os.path

import dirs



def read_conf_file_fake_header(conf_rel_file, fake_section='',
        conf_base_dir=dirs.get_conf_path()):
    """Read config file in configparser format, but insert a fake header for
    first section.  This is aimed at files that are close to configparser
    format, but do not have a section header for the first section.

    The fake section name is not important.

    Args:
      conf_rel_file (str): Relative file path to config file.
      fake_section (str): Fake section name, if needed.
      conf_base_dir (str): Base file path to use with relative path.  If not
        provided, this will use the absolute path of this module.

    Returns:
      config (configparser.ConfigParser): ConfigParser for file loaded.
    """
    conf_file = os.path.join(conf_base_dir, conf_rel_file)

    config = configparser.ConfigParser()
    file = open(conf_file, encoding="utf_8")
    config.read_file(itertools.chain(['[' + fake_section + ']'], file))

    return config



def read_conf_file(conf_rel_file, conf_base_dir=dirs.get_conf_path()):
    """Read config file in configparser format.

    Args:
      conf_rel_file (str): Relative file path to config file.
      conf_base_dir (str): Base file path to use with relative path.  If not
        provided, this will use the absolute path of this module.

    Returns:
      config (configparser.ConfigParser): ConfigParser for file loaded.
    """
    conf_file = os.path.join(conf_base_dir, conf_rel_file)

    config = configparser.ConfigParser()
    config.read(conf_file)

    return config
