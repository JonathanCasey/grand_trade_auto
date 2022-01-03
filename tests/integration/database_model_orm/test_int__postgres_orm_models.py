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

from grand_trade_auto.model import company
from grand_trade_auto.model import datafeed_src
from grand_trade_auto.model import exchange
from grand_trade_auto.model import model_meta



@pytest.fixture(name='datafeed_src_from_db')
def fixture_datafeed_src_from_db(pg_test_orm):
    """
    Creates a bare minimum datafeed_src entry in the database so it can be used
    for other models that require it as a foreign key.
    """
    init_data = {
        'config_parser': str(uuid.uuid4()),
    }
    conn = pg_test_orm._db.connect(False)

    datafeed_src.DatafeedSrc.add_direct(pg_test_orm, init_data, conn=conn)
    where = ('config_parser', model_meta.LogicOp.EQ, init_data['config_parser'])
    models = datafeed_src.DatafeedSrc.query_direct(pg_test_orm, 'model',
            where=where, conn=conn)
    conn.close()
    # Sanity check that there isn't a weird test collision
    assert len(models) == 1
    return models[0]



@pytest.mark.order(1)   # Model dependencies: datafeed_src
def test_int__model_crud__company(pg_test_orm, datafeed_src_from_db):
    """
    Tests that Company can be created, retrieved, updated, and deleted (in that
    order).

    Ensures compatibility between python and database representations of
    information.
    """
    # Ensure add works with all columns (except id)
    init_data = {
        'name': str(uuid.uuid4())[:50],
        'sector': str(uuid.uuid4())[:50],
        'industry_group': str(uuid.uuid4())[:50],
        'industry_category': str(uuid.uuid4())[:50],
        'cik': str(uuid.uuid4())[:10],
        'sic': str(uuid.uuid4())[:4],
        'datafeed_src_id': datafeed_src_from_db.id,
    }
    py_company = company.Company(pg_test_orm, init_data)
    py_company.add()

    # Ensure can pull exact model back from db and data format is valid
    where = ('name', model_meta.LogicOp.EQ, init_data['name'])
    models = company.Company.query_direct(pg_test_orm, 'model', where=where)
    assert len(models) == 1
    db_company = models[0]
    assert int(db_company.id) > 0
    for k, v in init_data.items():
        assert getattr(db_company, k) == v

    # Write same data back unchanged with all columns active
    db_company.update()

    # Delete this and confirm
    db_company.delete()
    models = company.Company.query_direct(pg_test_orm, 'model', where=where)
    assert len(models) == 0

    pg_test_orm._db._conn.close()



@pytest.mark.order(0)   # Model dependencies: None
def test_int__model_crud__datafeed_src(pg_test_orm):
    """
    Tests that DatafeedSrc can be created, retrieved, updated, and deleted (in
    that order).

    Ensures compatibility between python and database representations of
    information.
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
    assert int(db_datafeed_src.id) > 0
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



@pytest.mark.order(1)   # Model dependencies: datafeed_src
def test_int__model_crud__exchange(pg_test_orm, datafeed_src_from_db):
    """
    Tests that Exchange can be created, retrieved, updated, and deleted (in that
    order).

    Ensures compatibility between python and database representations of
    information.
    """
    # Ensure add works with all columns (except id)
    init_data = {
        'name': str(uuid.uuid4())[:50],
        'acronym': str(uuid.uuid4())[:50],
        'datafeed_src_id': datafeed_src_from_db.id,
    }
    py_exchange = exchange.Exchange(pg_test_orm, init_data)
    py_exchange.add()

    # Ensure can pull exact model back from db and data format is valid
    where = ('name', model_meta.LogicOp.EQ, init_data['name'])
    models = exchange.Exchange.query_direct(pg_test_orm, 'model', where=where)
    assert len(models) == 1
    db_exchange = models[0]
    assert int(db_exchange.id) > 0
    for k, v in init_data.items():
        assert getattr(db_exchange, k) == v

    # Write same data back unchanged with all columns active
    db_exchange.update()

    # Delete this and confirm
    db_exchange.delete()
    models = exchange.Exchange.query_direct(pg_test_orm, 'model', where=where)
    assert len(models) == 0

    pg_test_orm._db._conn.close()
