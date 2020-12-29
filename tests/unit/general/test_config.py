#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.config functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  APP_NAME (str): The name of the app as it appears in its folder name in the
    repo root.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging
import os.path

from grand_trade_auto.general import config



def test_read_conf_file_fake_header():
    """
    Tests that the `read_conf_file_fake_header()` will correctly read a file
    with no header, regardless of whether a fake header name was provided or the
    default was used.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_config')
    parser = config.read_conf_file_fake_header('mock_config_no_header.conf',
            conf_dir)
    assert parser['fake']['test key no header'] == 'test-val-no-header'
    assert parser['test-submod :: test-section']['test key str'] \
            == 'test-val-str'

    parser = config.read_conf_file_fake_header('mock_config_no_header.conf',
            conf_dir, 'new fake')
    assert parser['new fake']['test key no header'] == 'test-val-no-header'
    assert parser['test-submod :: test-section']['test key str'] \
            == 'test-val-str'



def test_read_conf_file():
    """
    Tests that the `read_conf_file()` will correctly read a file, checking a
    couple values.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_config')
    parser = config.read_conf_file('mock_config.conf', conf_dir)
    assert parser['test-section']['test key str'] == 'test-val-str'
    assert parser.getint('test-section', 'test key int') == 123



def test_get_matching_secrets_id():
    """
    Tests the `get_matching_secrets_id()`.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'test_config')

    main_cp = config.read_conf_file('mock_config.conf', conf_dir)
    secrets_cp = config.read_conf_file_fake_header(
            'mock_config_no_header.conf', conf_dir)
    main_id = main_cp.sections()[0]

    section_id = config.get_matching_secrets_id(secrets_cp, 'test-submod',
            main_id)
    assert section_id == 'test-submod :: test-section'

    section_id = config.get_matching_secrets_id(secrets_cp, 'test-submod',
            'bad-id')
    assert section_id is None

    section_id = config.get_matching_secrets_id(secrets_cp, 'bad-submod',
            main_id)
    assert section_id is None



def test_level_filter(caplog, capsys):
    """
    Tests `LevelFilter` entirely.

    Note that caplog does NOT respect filters added to handlers, so results in
    records/record_tuples must then also be checked against capsys to confirm
    logging actually went through or did not as expected (stderr used for all as
    default).
    """
    filter_above_info = config.LevelFilter(min_exc_level=logging.INFO)
    filter_above_info_upto_warning = config.LevelFilter('info', 30)
    filter_upto_warning = config.LevelFilter(max_inc_level='WARNING')

    handlers = {}
    loggers = {}
    test_levels = ['INFO', 'WARNING', 'ERROR']
    for level in test_levels:
        handlers[level] = logging.StreamHandler()
        handlers[level].setLevel(level)

        loggers[level] = logging.getLogger(f'test logger {level.lower()}')
        loggers[level].addHandler(handlers[level])
        loggers[level].setLevel(level)

    caplog.set_level(logging.DEBUG)

    caplog.clear()
    for level in test_levels:
        loggers[level].info(f'1. test, msg info, log {level}')
    assert caplog.record_tuples == [
            ('test logger info', logging.INFO, '1. test, msg info, log INFO'),
    ]
    assert '1. test, msg info, log INFO' in capsys.readouterr().err

    caplog.clear()
    for level in test_levels:
        loggers[level].warning(f'2. test, msg warning, log {level}')
    assert caplog.record_tuples == [
            ('test logger info', logging.WARNING, '2. test, msg warning, log INFO'),
            ('test logger warning', logging.WARNING, '2. test, msg warning, log WARNING'),
    ]
    stderr = capsys.readouterr().err
    assert '2. test, msg warning, log INFO' in stderr
    assert '2. test, msg warning, log WARNING' in stderr

    caplog.clear()
    handlers['INFO'].addFilter(filter_above_info)
    for level in test_levels:
        loggers[level].info(f'3. test, msg info, log {level}')
        loggers[level].warning(f'3. test, msg warning, log {level}')
    assert caplog.record_tuples == [
            ('test logger info', logging.INFO, '3. test, msg info, log INFO'),
            ('test logger info', logging.WARNING, '3. test, msg warning, log INFO'),
            ('test logger warning', logging.WARNING, '3. test, msg warning, log WARNING'),
    ]
    stderr = capsys.readouterr().err
    assert '3. test, msg info, log INFO' not in stderr
    assert '3. test, msg warning, log INFO' in stderr
    assert '3. test, msg warning, log WARNING' in stderr

    handlers['INFO'].removeFilter(filter_above_info)
    caplog.clear()
    handlers['INFO'].addFilter(filter_above_info_upto_warning)
    handlers['WARNING'].addFilter(filter_upto_warning)
    for level in test_levels:
        loggers[level].info(f'4. test, msg info, log {level}')
        loggers[level].warning(f'4. test, msg warning, log {level}')
        loggers[level].error(f'4. test, msg error, log {level}')
    assert caplog.record_tuples == [
            ('test logger info', logging.INFO, '4. test, msg info, log INFO'),
            ('test logger info', logging.WARNING, '4. test, msg warning, log INFO'),
            ('test logger info', logging.ERROR, '4. test, msg error, log INFO'),
            ('test logger warning', logging.WARNING, '4. test, msg warning, log WARNING'),
            ('test logger warning', logging.ERROR, '4. test, msg error, log WARNING'),
            ('test logger error', logging.ERROR, '4. test, msg error, log ERROR'),
    ]
    stderr = capsys.readouterr().err
    assert '4. test, msg info, log INFO' not in stderr
    assert '4. test, msg warning, log INFO' in stderr
    assert '4. test, msg error, log INFO' not in stderr
    assert '4. test, msg warning, log WARNING' in stderr
    assert '4. test, msg error, log WARNING' not in stderr
    assert '4. test, msg error, log ERROR' in stderr
