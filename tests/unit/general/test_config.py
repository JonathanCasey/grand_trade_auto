#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.config functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Attributes:
  APP_NAME (str): The name of the app as it appears in its folder name in the
    repo root.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import os.path

from grand_trade_auto.general import config



def test_read_conf_file_fake_header():
    """Tests that the `read_conf_file_fake_header()` will correctly read a file
    with no header, regardless of whether a fake header name was provided or the
    default was used.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'mock')
    parser = config.read_conf_file_fake_header('mock_config_no_header.conf',
            conf_dir)
    assert parser['fake']['test key no header'] == 'test-val-no-header'
    assert parser['test-section']['test key str'] == 'test-val-str'

    parser = config.read_conf_file_fake_header('mock_config_no_header.conf',
            conf_dir, 'new fake')
    assert parser['new fake']['test key no header'] == 'test-val-no-header'
    assert parser['test-section']['test key str'] == 'test-val-str'



def test_read_conf_file():
    """Tests that the `read_conf_file()` will correctly read a file, checking a
    couple values.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    conf_dir = os.path.join(this_dir, 'mock')
    parser = config.read_conf_file('mock_config.conf', conf_dir)
    assert parser['test-section']['test key str'] == 'test-val-str'
    assert parser.getint('test-section', 'test key int') == 123
