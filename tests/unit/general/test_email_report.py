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
import smtplib

import pytest

from grand_trade_auto.general import config
from grand_trade_auto.general import email_report
from grand_trade_auto.general.exceptions import *   # pylint: disable=wildcard-import, unused-wildcard-import



class MockSmtp:
    """
    Simple mock object to replace smtplib.SMTP and its relevant methods.
    """
    def __init__(self, *args, **kwargs):    # pylint: disable=unused-argument
        """
        Creates a dummy object.
        """
        return

    def ehlo(self, *args, **kwargs):        # pylint: disable=unused-argument, no-self-use
        """
        Dummy ehlo.  Does nothing.
        """
        return

    def starttls(self, *args, **kwargs):    # pylint: disable=unused-argument, no-self-use
        """
        Dummy start TLS.  Does nothing.
        """
        return

    def login(self, *args, **kwargs):       # pylint: disable=unused-argument, no-self-use
        """
        Dummy login.  Does nothing.
        """
        return

    def sendmail(self, *args, **kwargs):    # pylint: disable=unused-argument, no-self-use
        """
        Dummy send mail.  Does nothing.
        """
        return

    def quit(self, *args, **kwargs):        # pylint: disable=unused-argument, no-self-use
        """
        Dummy quit.  Does nothing.
        """
        return



@pytest.fixture(name='mock_load_email_conf_dummy')
def fixture_mock_load_email_conf_dummy(monkeypatch):
    """
    Replaces the `load_email_conf()` with one that will return dummy values.
    """

    def mock_load_data():
        """
        Replaces the `load_email_conf()` with one that will return dummy values.
        """
        return {
            'server': 'fake server',
            'port': 'fake port',
            'sender': 'fake sender',
            'password': 'fake password',
            'sender_name': 'fake sender name',
            'recipients': [
                'fake recipient 1',
                'fake recipient 2',
            ],
        }

    monkeypatch.setattr(email_report, 'load_email_conf', mock_load_data)



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



def test_send_email(monkeypatch,
        mock_load_email_conf_dummy):           # pylint: disable=unused-argument
    """
    Tests `send_email()`.

    Does not actually send any email -- this must be tested outside of unit
    tests to ensure it works.  A convenience for doing this has been added to
    `email_report.py` that allows that module to be called directly solely for
    such a test.
    """
    def mock_load_email_conf_fail():
        """
        Replaces the `load_email_conf()` with one that will raise an exception.
        """
        raise Exception('Fake failure.')


    def mock_quit_fail():
        """
        Mocks the quit call of SMTP (or any) to raise an exception.
        """
        raise Exception('Unit test simulated failure.')


    monkeypatch.setattr(smtplib, 'SMTP', MockSmtp)


    email_report.send_email('test subject', 'test body')
    # Continuing past this point indicates this test above passed


    monkeypatch.setattr(MockSmtp, 'quit', mock_quit_fail)

    with pytest.raises(EmailConnectionError) as ex:
        email_report.send_email('s', 'b')
    assert 'Email send connection error.' in str(ex.value)


    monkeypatch.setattr(email_report, 'load_email_conf',
            mock_load_email_conf_fail)

    with pytest.raises(EmailConfigError) as ex:
        email_report.send_email('s', 'b')
    assert 'Email config load failed.' in str(ex.value)
