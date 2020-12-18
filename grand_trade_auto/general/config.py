#!/usr/bin/env python3
"""
This module handles access to the configuration files.  The configuration
files--including the environment files--are accessed by the other python scripts
through this file.

This is setup such that other files need only call the `get()` functions, and
all the loading and caching will happen automatically internal to this file.

As of right now, this is hard-coded to access configuration files at a specific
name and path.

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import configparser
import itertools
import logging
import logging.config
import os.path

from grand_trade_auto.general import dirs



def read_conf_file_fake_header(conf_rel_file,
        conf_base_dir=dirs.get_conf_path(), fake_section='fake',):
    """
    Read config file in configparser format, but insert a fake header for
    first section.  This is aimed at files that are close to configparser
    format, but do not have a section header for the first section.

    The fake section name is not important.

    Args:
      conf_rel_file (str): Relative file path to config file.
      conf_base_dir (str): Base file path to use with relative path.  If not
        provided, this will use the absolute path of this module.
      fake_section (str): Fake section name, if needed.

    Returns:
      parser (ConfigParser): ConfigParser for file loaded.
    """
    conf_file = os.path.join(conf_base_dir, conf_rel_file)

    parser = configparser.ConfigParser()
    file = open(conf_file, encoding="utf_8")
    parser.read_file(itertools.chain(['[' + fake_section + ']'], file))

    return parser



def read_conf_file(conf_rel_file, conf_base_dir=dirs.get_conf_path()):
    """
    Read config file in configparser format.

    Args:
      conf_rel_file (str): Relative file path to config file.
      conf_base_dir (str): Base file path to use with relative path.  If not
        provided, this will use the absolute path of this module.

    Returns:
      parser (ConfigParser): ConfigParser for file loaded.
    """
    conf_file = os.path.join(conf_base_dir, conf_rel_file)

    parser = configparser.ConfigParser()
    parser.read(conf_file)

    return parser



def get_matching_secrets_id(secrets_cp, submod, main_id):
    """
    Retrieves the section name (ID) for in the .secrets.conf that matches the
    submodule and main config ID provided.

    Args:
      secrets_cp (ConfigParser): A config parser for the .secrets.conf file
        already loaded.
      submod (str): The name of the submodule that should be the prefix in the
        section name for this in the .secrets.conf file.
      main_id (str): The name of section from the relevant submodule's config to
        ID this element.

    Returns:
      (str or None): The name of the matching section in the .secrets.conf; or
        None if no match.
    """
    for secrets_section_name in secrets_cp:
        try:
            submod_found, id_found = secrets_section_name.split('::')
            if submod_found.strip().lower() == submod.strip().lower() \
                    and id_found.strip().lower() == main_id.strip().lower():
                return secrets_section_name
        except ValueError:
            continue
    return None



def init_logger(override_log_level=None):
    """
    Initializes the logger(s).  This is meant to be called once per main entry.
    This does not alter that each module should be getting the logger for their
    module name, most likely from the root logger.

    Args:
      override_log_level (str): The log level to override and set for the root
        logger as well as the specified handlers from the
        `cli arg level override` section of `logger.conf`.  In addition to the
        standard logger level names and the `disabled` level added by this app,
        the names `all` and `verbose` can also be used for `notset` to get
        everything.
    """
    logging.addLevelName(99, 'DISABLED')
    logging.config.fileConfig(os.path.join(dirs.get_conf_path(), 'logger.conf'),
            disable_existing_loggers=False)

    if override_log_level is not None:
        new_level = override_log_level.upper()
        if new_level in ['ALL', 'VERBOSE']:
            new_level = 'NOTSET'

        root_logger = logging.getLogger()
        root_logger.setLevel(new_level)

        conf_file = os.path.join(dirs.get_conf_path(), 'logger.conf')
        logger_cp = configparser.RawConfigParser()
        logger_cp.read(conf_file)

        handler_names = [h.strip() for h in \
                logger_cp['cli arg level override']['handler keys'].split(',')]

        for h_existing in root_logger.handlers:
            # Until v3.10, handler name not stored from fileConfig :(
            # Will attempt to match on some other parameters, but not perfectly
            for h_conf in [logger_cp[f'handler_{h}'] for h in handler_names]:
                if type(h_existing).__name__ != h_conf['class']:
                    continue

                if logging.getLevelName(h_existing.level) \
                        != h_conf['level'].strip().upper():
                    continue

                h_conf_fmt = logger_cp[ \
                        f'formatter_{h_conf["formatter"]}']['format'].strip()
                if h_existing.formatter._fmt \
                        != h_conf_fmt:  # pylint: disable=protected-access
                    continue

                h_existing.setLevel(new_level)
