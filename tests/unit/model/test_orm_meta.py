#!/usr/bin/env python3
"""
Tests the grand_trade_auto.model.orm_meta functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  logger (Logger): Logger for this module (used for testing).

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import logging

from grand_trade_auto.model import orm_meta



logger = logging.getLogger(__name__)



class MockOrmChild(orm_meta.Orm):
    """"
    Simple mock class to subclass Orm.
    """
    def _create_schema_datafeed_src(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_datafeed_src()')

    def add(self, model_cls, data):
        """
        Not needed / will not be used.
        """

    def update(self, model_cls, data, where):
        """
        Not needed / will not be used.
        """

    def delete(self, model_cls, where, really_delete_all=False):
        """
        Not needed / will not be used.
        """

    def query(self, model_cls, return_as, columns_to_return=None,
            where=None, limit=None, order=None):
        """
        Not needed / will not be used.
        """



def test_init():
    """
    Tests the `__init__()` method in `Orm`.
    """
    mock_orm = MockOrmChild('fake db')
    assert mock_orm._db == 'fake db'



def test_create_schemas(caplog):
    """
    Tests the `create_schemas()` method in `Orm`.
    """
    caplog.set_level(logging.INFO)

    mock_orm = MockOrmChild(None)
    caplog.clear()
    mock_orm.create_schemas()
    assert caplog.record_tuples == [
        ('tests.unit.model.test_orm_meta', logging.INFO,
            'Called _create_schema_datafeed_src()')
    ]
