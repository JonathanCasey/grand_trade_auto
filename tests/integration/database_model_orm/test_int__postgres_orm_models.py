#!/usr/bin/env python3
"""
Tests the integration between:
- all models in the grand_trade_auto.model subpackage
- grand_trade_auto.orm.postgres_orm
- grand_trade_auto.database.postgres

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2022 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import uuid

import pytest

from grand_trade_auto.model import datafeed_src
from grand_trade_auto.model import model_meta



@pytest.mark.order(0)   # Model dependencies: None
def test_int__model_crud__datafeed_src(pg_test_orm):
    """
    Tests that DatafeedSrc can be created, retrieved, updated, and deleted (in
    that order).  Ensures compatibility between python and database
    representations of information.
    """
    # Ensure add works with all columns (except id)
    init_data = {
        'config_parser': str(uuid.uuid4()),
        'is_init_complete': False,
        'progress_marker': str(uuid.uuid4()),
    }
    py_datafeed_src = datafeed_src.DatafeedSrc(pg_test_orm, init_data)
    py_datafeed_src.add()

    # Ensure can pull exact model back from db and data format is valid
    where = ('config_parser', model_meta.LogicOp.EQ, init_data['config_parser'])
    models = datafeed_src.DatafeedSrc.query_direct(pg_test_orm, 'model',
            where=where)
    assert len(models) == 1
    db_datafeed_src = models[0]
    assert db_datafeed_src.id is not None
    for k, v in init_data.items():
        assert getattr(db_datafeed_src, k) == v

    # Write same data back unchanged with all columns active
    db_datafeed_src.update()

    # Delete this and confirm
    db_datafeed_src.delete()
    models = datafeed_src.DatafeedSrc.query_direct(pg_test_orm, 'model',
            where=where)
    assert len(models) == 0

    pg_test_orm._db._conn.close()
