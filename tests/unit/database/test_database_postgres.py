#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.database_postgres functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.database import database_postgres
from grand_trade_auto.database import databases



def test_load_from_config():
    """
    Tests the `load_from_config()` method in the `DatabasePostgres` class.

    TODO: This should load its own conf files and test directly; but good enough
    for now.
    """
    db_handle = databases.get_database_from_config('test', 'postgres')
    assert db_handle is not None



def test_get_type_names():
    """
    Tests the `get_type_names()` method in the `DatabasePostgres` class.  Not an
    exhaustive test.
    """
    assert 'postgres' in database_postgres.DatabasePostgres.get_type_names()
    assert 'not-postgres' not in \
            database_postgres.DatabasePostgres.get_type_names()
