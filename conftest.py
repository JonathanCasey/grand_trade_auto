#!/usr/bin/env python3
"""
Configures pytest as needed.  This file can be left completely empty but must
exist.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import pytest



def pytest_addoption(parser):
    """
    Adds additional CLI options for invoking `pytest`.

    https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_addoption

    Args:
      parser (Parser): Parser to which options and ini-file values can be added.
    """
    parser.addoption('--run-only-alters-db-schema',
            action='store_true',
            default=False,
            help='ONLY run tests requiring alterations to database schema beyond'
                + ' simple initialization.',
    )
    parser.addoption('--skip-alters-db-schema',
            action='store_true',
            default=False,
            help='SKIP running tests requiring alterations to database schema'
                + ' beyond simple initialization.',
    )



def pytest_configure(config):
    """
    Performs initial configuration after CLI options have been parsed.

    https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_configure

    Args:
      config (Config): Config object to which configurations can be added.  See
        pytest docs: https://docs.pytest.org/en/6.2.x/reference.html#config
    """
    config.addinivalue_line('markers',
            'alters_db_schema: Mark test as will alter the database scheme'
                +' beyond simple initialization (and should likely be run'
                + ' separately.')



def pytest_collection_modifyitems(config, items):
    """
    After collection has been performed, can filter, reorder, or otherwise
    modify test items.

    https://docs.pytest.org/en/6.2.x/reference.html#pytest.hookspec.pytest_collection_modifyitems

    Modifications implemented:
    - `--run-only-alters-db-schema`: Only run tests marked to alter db schema.
    - `--skip-alters-db-schema`: Skip tests marked to alter db schema.

    Args:
      config (Config): Config object containing the pytest configuration.  See
        pytest docs: https://docs.pytest.org/en/6.2.x/reference.html#config
      items ([Items]): The list of pytest options collected that can be
        modified.  See docs:
        https://docs.pytest.org/en/6.2.x/reference.html#pytest.Item .  The Node
        docs from which it inherits are also very helpful:
        https://docs.pytest.org/en/6.2.x/reference.html#node
    """
    if config.getoption('--run-only-alters-db-schema'):
        skip_non_alters_db_schema = pytest.mark.skip(
                reason='Must omit --run-only-alters-db-schema option to run')
        for item in items:
            if 'alters_db_schema' not in item.keywords:
                item.add_marker(skip_non_alters_db_schema)

    if config.getoption('--skip-alters-db-schema'):
        skip_alters_db_schema = pytest.mark.skip(
                reason='Must omit --skip-alters-db-schema option to run')
        for item in items:
            if 'alters_db_schema' in item.keywords:
                item.add_marker(skip_alters_db_schema)
