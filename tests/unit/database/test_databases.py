#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.databases functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import pytest

from grand_trade_auto.database import databases



def test_load_and_set_main_database_from_config():
    """
    Tests that the `load_and_set_main_database_from_config()` method.
    """
    with pytest.raises(AssertionError):
        databases.load_and_set_main_database_from_config('invalid-env')
    assert databases._DB_HANDLE is None

    databases.load_and_set_main_database_from_config('test', 'postgres')
    assert databases._DB_HANDLE is not None
    assert databases._DB_HANDLE._check_if_db_exists()

    with pytest.raises(AssertionError):
        databases.load_and_set_main_database_from_config('test')
    assert databases._DB_HANDLE is not None

    # Cleanup
    databases._DB_HANDLE._drop_db()
    assert not databases._DB_HANDLE._check_if_db_exists()



def test_get_database_from_config():
    """
    Tests that the `_get_database_from_config()` method.
    """
    assert databases._get_database_from_config('invalid-env') is None
    assert databases._get_database_from_config('test', 'invalid-type') is None
    assert databases._get_database_from_config('test') is not None
    assert databases._get_database_from_config('test', 'postgres') is not None
