#!/usr/bin/env python3
"""
Tests the grand_trade_auto.orm.orm_meta functionality.

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

from grand_trade_auto.orm import orm_meta



logger = logging.getLogger(__name__)



class MockOrmChild(orm_meta.Orm):
    """"
    Simple mock class to subclass Orm.
    """
    def _create_schema_enum_currency(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_enum_currency()')

    def _create_schema_enum_market(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_enum_market()')

    def _create_schema_enum_price_frequency(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_enum_price_frequency()')

    def _create_schema_table_company(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_table_company()')

    def _create_schema_table_datafeed_src(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_table_datafeed_src()')

    def _create_schema_table_exchange(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_table_exchange()')

    def _create_schema_table_security(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_table_security()')

    def _create_schema_table_security_price(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_table_security_price()')

    def _create_schema_table_stock_adjustment(self):
        """
        Log something so it can be traced that this was called.
        """
        logger.info('Called _create_schema_table_stock_adjustment()')

    def add(self, model_cls, data, **kwargs):
        """
        Not needed / will not be used.
        """

    def update(self, model_cls, data, where, **kwargs):
        """
        Not needed / will not be used.
        """

    def delete(self, model_cls, where, really_delete_all=False, **kwargs):
        """
        Not needed / will not be used.
        """

    def query(self, model_cls, return_as, columns_to_return=None,
            where=None, limit=None, order=None, **kwargs):
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
        ('tests.unit.orm.test_orm_meta', logging.INFO,
            'Called _create_schema_enum_currency()'),
        ('tests.unit.orm.test_orm_meta', logging.INFO,
            'Called _create_schema_enum_market()'),
        ('tests.unit.orm.test_orm_meta', logging.INFO,
            'Called _create_schema_enum_price_frequency()'),
        ('tests.unit.orm.test_orm_meta', logging.INFO,
            'Called _create_schema_table_datafeed_src()'),
        ('tests.unit.orm.test_orm_meta', logging.INFO,
            'Called _create_schema_table_exchange()'),
        ('tests.unit.orm.test_orm_meta', logging.INFO,
            'Called _create_schema_table_company()'),
        ('tests.unit.orm.test_orm_meta', logging.INFO,
            'Called _create_schema_table_security()'),
        ('tests.unit.orm.test_orm_meta', logging.INFO,
            'Called _create_schema_table_security_price()'),
        ('tests.unit.orm.test_orm_meta', logging.INFO,
            'Called _create_schema_table_stock_adjustment()'),
    ]
