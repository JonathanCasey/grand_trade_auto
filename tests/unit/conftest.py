#!/usr/bin/env python3
"""
Configures pytest as needed.  This file normally does not need to exist, but is
used here to share and configure items for the /tests/unit subpackage and all
descendents.

Module Attributes:
  _TEST_PG_DB_ID (str): The name/ID of the section to pull from the database
    conf file to use as the test database configuration.
  _TEST_PG_ENV (str): The name of environment to use for testing.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import pytest

from grand_trade_auto.database import databases



_TEST_PG_DB_ID = 'postgres-test'
_TEST_PG_ENV = 'test'



@pytest.fixture(scope='session', autouse=True)
def fixture_create_test_db():
    """
    Creates the test database to be used for all tests.

    This is NOT to be relied upon for any tests marked as alters_db_schema, but
    they should consider that this will create the database.
    """
    test_db = databases._get_database_from_config(_TEST_PG_DB_ID, _TEST_PG_ENV)
    test_db._drop_db() # Ensure cleared to start
    test_db.create_db()
    yield
    test_db._drop_db()



@pytest.fixture(name='pg_test_db')
def fixture_pg_test_db():
    """
    Gets the test database handle for postgres.

    Returns:
      (Postgres): The test postgres database handle.
    """
    # This also ensures its support was added to databases.py
    return databases._get_database_from_config(_TEST_PG_DB_ID, _TEST_PG_ENV)
