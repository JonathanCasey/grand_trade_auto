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



class LevelFilter(logging.Filter):
    """
    A logging filter for the level to set min and max log levels for a handler.
    While the min level is redundant given logging already implements this with
    the base level functionality, the max level adds a new control.

    Class Attributes:
      N/A

    Instance Attributes:
      _min_levelno (int or None): The min log level to be included (inclusive).
        Can be None to skip min level check.
      _max_levelno (int or None): The max log level to be included (inclusive).
        Can be None to skip max level check.
    """
    def __init__(self, min_level=None, max_level=None):
        """
        Creates the level filter.

        Args:
          min_level (int/str/None): The min log level to be inclued (inclusive).
            Can be provided as the int level number or as the level name.  Can
            be omitted/None to disable filtering the min level.
          max_level (int/str/None): The max log level to be inclued (inclusive).
            Can be provided as the int level number or as the level name.  Can
            be omitted/None to disable filtering the max level.
        """
        try:
            self._min_levelno = int(min_level)
        except ValueError:
            # Level name dict is bi-directional lookup -- See python source
            self._min_levelno = logging.getLevelName(min_level.upper())
        except TypeError:
            self._min_levelno = None

        try:
            self._max_levelno = int(max_level)
        except ValueError:
            # Level name dict is bi-directional lookup -- See python source
            self._max_levelno = logging.getLevelName(max_level.upper())
        except TypeError:
            self._max_levelno = None

        super().__init__()



    def filter(self, record):
        """
        Filters the provided record according to the logic in this method.

        Args:
          record (LogRecord): The log record that is being checked whether to
            log.

        Returns:
          (bool): True if should log; False to drop.
        """
        if self._min_levelno is not None and record.levelno < self._min_levelno:
            return False
        if self._max_levelno is not None and record.levelno > self._max_levelno:
            return False
        return True



def init_logger(override_log_level=None):
    """
    Initializes the logger(s).  This is meant to be called once per main entry.
    This does not alter that each module should be getting the logger for their
    module name, most likely from the root logger.

    This will apply the override log level if applicable.

    It will also check for the boundary level between stdout and stderr
    handlers, if applicable, and set a filter level.  This must be set in the
    `logging.conf` and must have both a stdout and a stderr handler; but once
    true, will apply to ALL stdout and ALL stderr StreamHandlers!

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

        stdout_handlers = []
        stderr_handlers = []
        for h_existing in root_logger.handlers:
            for h_conf in [logger_cp[f'handler_{h}'] for h in handler_names]:
                # Until v3.10, handler name not stored from fileConfig :(
                # Will attempt match on some other parameters, but not perfectly
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

            if isinstance(h_existing, logging.StreamHandler):
                if h_existing.stream.name == '<stdout>':
                    stdout_handlers.append(h_existing)
                elif h_existing.stream.name == '<stderr>':
                    stderr_handlers.append(h_existing)

        if len(stdout_handlers) > 0 and len(stderr_handlers) > 0:
            for h_stdout in stdout_handlers:
                h_stdout.addFilter(LevelFilter(max_level='info'))
            for h_stderr in stderr_handlers:
                h_stderr.addFilter(LevelFilter(min_level='warning'))
