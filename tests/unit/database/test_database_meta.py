#!/usr/bin/env python3
"""
Tests the grand_trade_auto.database.database_meta functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.database import database_meta



def test_matches_id_criteria():
    """
    Tests the `matches_id_criteria()` method of `Database`.
    """

    class MockDatabaseChild(database_meta.Database):
        """"
        Simple mock object to subclass database.
        """

        @classmethod
        def load_from_config(cls, db_cp, db_id, secrets_id):
            """
            Not needed / will not be used.
            """
            return

        @classmethod
        def get_type_names(cls):
            """
            Need at least 1 name to match.
            """
            return ['mock_type']

        def create_db(self):
            """
            Not needed / will not be used.
            """
            return

    db = MockDatabaseChild('mock_env', 'mock_cp_db_id', 'mock_cp_secrets_id',
            'mock_host', -1, 'mock_database')
    assert not db.matches_id_criteria('invalid-db-id')
    assert db.matches_id_criteria('mock_cp_db_id')
    assert not db.matches_id_criteria('mock_cp_db_id', 'invalid-env')
    assert db.matches_id_criteria('mock_cp_db_id', 'mock_env')
    assert not db.matches_id_criteria('mock_cp_db_id', db_type='invalid-type')
    assert db.matches_id_criteria('mock_cp_db_id', db_type='mock_type')
    assert not db.matches_id_criteria('mock_cp_db_id', 'invalid-env',
            'mock_type')
    assert not db.matches_id_criteria('mock_cp_db_id', 'mock_env',
            'invalid-type')
    assert db.matches_id_criteria('mock_cp_db_id', 'mock_env', 'mock_type')
