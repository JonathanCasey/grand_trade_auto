#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.databases functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Attributes:
  APP_NAME (str): The name of the app as it appears in its folder name in the
    repo root.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.database import databases
from grand_trade_auto.general import config



def test_load_databases_from_config(monkeypatch):
    """
    Tests that the `load_databases_from_config()` method works properly.
    """
    original_read_conf_file = config.read_conf_file

    def mock_read_conf_file(conf_rel_file):
        """
        Overrides `read_conf_file()` (taking only arguments relevant to calls in
        this test), to alter values before returning.

        See grand_trade_auto.general.config.read_conf_file() for rest of args
        and returns.
        """
        parser = original_read_conf_file(conf_rel_file)
        for section in parser.sections():
            if 'database' in parser[section]:
                parser[section]['database'] = parser[section]['database'] \
                            + '_TEST'
        return parser


    monkeypatch.setattr(config, 'read_conf_file', mock_read_conf_file)


    databases.load_databases_from_config('test')
    assert databases.DB_HANDLE is not None
    # assert databases.DB_HANDLE.database == 'grand_trade_auto'
