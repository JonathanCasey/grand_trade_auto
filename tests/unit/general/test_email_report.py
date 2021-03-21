#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.email_report functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import os.path

from grand_trade_auto.general import config
from grand_trade_auto.general import email_report



def test_load_email_conf(monkeypatch):
    """
    Tests `load_email_conf()`.
    """
    this_dir = os.path.dirname(os.path.realpath(__file__))
    test_conf_dir = os.path.join(this_dir, 'test_config')

    orig_read_conf_file_fake_header = config.read_conf_file_fake_header
    orig_read_conf_file = config.read_conf_file


    def mock_read_conf_file_fake_header(file, fake_section='fake'):
        """
        Replaces the `read_conf_file_fake_header()`.  `conf_base_dir` will be
        overridden.
        """
        return orig_read_conf_file_fake_header(file, test_conf_dir,
                fake_section)


    def mock_read_conf_file(file):
        """
        Replaces the `read_conf_file()`.  `conf_base_dir` will be overridden.
        """
        return orig_read_conf_file(file, test_conf_dir)


    monkeypatch.setattr(config, 'read_conf_file_fake_header',
            mock_read_conf_file_fake_header)
    monkeypatch.setattr(config, 'read_conf_file', mock_read_conf_file)


    data = email_report.load_email_conf()

    assert data['server'] == 'fake-hoest.nowhere.com'
    assert data['port'] == 555 or data['port'] == '555'
    assert data['sender'] == 'fake-username@nowhere.com'
    assert data['password'] == 'fake-password'
    assert data['sender_name'] == 'Fake Send Name <fake-send-name@nowhere.com>'
    assert len(data['recipients']) == 2
    assert data['recipients'][0] == 'Fake User 1 <fake-user-1@nowhere.com>'
    assert data['recipients'][1] == 'Fake User 2 <fake-user-2@nowhere.com>'
