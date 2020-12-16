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
import pytest

from grand_trade_auto.database import databases



def test_load_databases_from_config():
    """
    Tests that the `load_databases_from_config()` method works properly,
    including in unintended paths.
    """
    with pytest.raises(AssertionError):
        databases.load_databases_from_config('invalid-env')
    assert databases.DB_HANDLE is None

    databases.load_databases_from_config('test')
    assert databases.DB_HANDLE is not None

    with pytest.raises(AssertionError):
        databases.load_databases_from_config('test')
