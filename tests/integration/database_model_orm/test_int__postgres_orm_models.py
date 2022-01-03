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
from grand_trade_auto.model import security



def _create_and_get_model_from_db(pg_test_orm, model_cls, init_data, col_match):
    """
    Creates a model, adds it to the database, then retrieves it back from the
    database based on the provided configuration information.  This allows the
    usage of generated columns such as the typical `id`.  Intended to be called
    from fixtures, but could be called in general.

    Args:
      pg_test_orm (PostgresOrm): A PostgresOrm to use, likely the fixture.
      model_cls (Class<Model<>>): The reference to a subclass of `Model` that is
        to be created, added to db, then retrieved back.
      init_data ({str:str/int/etc}): The data to initialize the model when
        adding to the database.
      col_match (str): The column on which to match this model in the database
        in order to concisely retrieve it.  Likely the longest field that uses a
        string/uuid, but may need to improvise sometimes.  Can be anything, but
        it will always be a strict equals comparison.

    Returns:
      (model_cls): The model with the provided data, but as it is retrieved back
        from the database with any generated fields also populated.
    """
    conn = pg_test_orm._db.connect(False)
    model_cls.add_direct(pg_test_orm, init_data, conn=conn)
    where = (col_match, model_meta.LogicOp.EQ, init_data[col_match])
    models = model_cls.query_direct(pg_test_orm, 'model', where=where,
            conn=conn)
    conn.close()
    # Sanity check that there isn't a weird test collision
    assert len(models) == 1
    return models[0]



@pytest.fixture(name='company_from_db')
def fixture_company_from_db(pg_test_orm, datafeed_src_from_db):
    """
    Creates a bare minimum company entry in the database so it can be used for
    other models that require it as a foreign key.
    """
    init_data = {
        'name': str(uuid.uuid4())[:50],
        'datafeed_src_id': datafeed_src_from_db.id,
    }
    return _create_and_get_model_from_db(pg_test_orm, company.Company,
            init_data, 'name')



@pytest.fixture(name='datafeed_src_from_db')
def fixture_datafeed_src_from_db(pg_test_orm):
    """
    Creates a bare minimum datafeed_src entry in the database so it can be used
    for other models that require it as a foreign key.
    """
    init_data = {
        'config_parser': str(uuid.uuid4()),
    }
    return _create_and_get_model_from_db(pg_test_orm, datafeed_src.DatafeedSrc,
            init_data, 'config_parser')



@pytest.fixture(name='exchange_from_db')
def fixture_exchange_from_db(pg_test_orm, datafeed_src_from_db):
    """
    Creates a bare minimum exchange entry in the database so it can be used for
    other models that require it as a foreign key.
    """
    init_data = {
        'name': str(uuid.uuid4())[:50],
        'acronym': str(uuid.uuid4())[:50],
        'datafeed_src_id': datafeed_src_from_db.id,
    }
    return _create_and_get_model_from_db(pg_test_orm, exchange.Exchange,
            init_data, 'name')



def _test_int__model_crud(pg_test_orm, model_cls, init_data, col_match):
    """
    A generic set of steps to run through to test that the given model can be
    created, retrieved, updated, and deleted (in that order).

    Ensures compatibility between python and database representations of
    information.

    This will use the cached connection of the Orm's db, so the caller must
    handle closing that connection.

    Args:
      pg_test_orm (PostgresOrm): A PostgresOrm to use, likely the fixture.
      model_cls (Class<Model<>>): The reference to a subclass of `Model` that is
        to be CRUD tested.
      init_data ({str:str/int/etc}): The data to initialize the model when
        adding to the database.
      col_match (str): The column on which to match this model in the database
        in order to concisely retrieve it.  Likely the longest field that uses a
        string/uuid, but may need to improvise sometimes.  Can be anything, but
        it will always be a strict equals comparison.
    """
    # Ensure add works with all columns (except id / auto-generated)
    py_model = model_cls(pg_test_orm, init_data)
    py_model.add()

    # Ensure can pull exact model back from db and data format is valid
    where = (col_match, model_meta.LogicOp.EQ, init_data[col_match])
    models = model_cls.query_direct(pg_test_orm, 'model', where=where)
    assert len(models) == 1
    db_model = models[0]
    assert int(db_model.id) > 0
    for k, v in init_data.items():
        assert getattr(db_model, k) == v

    # Ensure can write same data back unchanged with all columns active
    db_model.update()

    # Ensure can delete this and confirm
    db_model.delete()
    models = model_cls.query_direct(pg_test_orm, 'model', where=where)
    assert len(models) == 0



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
    _test_int__model_crud(pg_test_orm, company.Company, init_data, 'name')
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
    _test_int__model_crud(pg_test_orm, datafeed_src.DatafeedSrc, init_data,
            'config_parser')
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
    _test_int__model_crud(pg_test_orm, exchange.Exchange, init_data, 'name')
    pg_test_orm._db._conn.close()



@pytest.mark.order(2)   # Model dependencies: company, datafeed_src, exchange
def test_int__model_crud__security(pg_test_orm, company_from_db,
        datafeed_src_from_db, exchange_from_db):
    """
    Tests that Security can be created, retrieved, updated, and deleted (in that
    order).

    Ensures compatibility between python and database representations of
    information.
    """
    # Ensure add works with all columns (except id)
    init_data = {
        'exchange_id': exchange_from_db.id,
        'ticker': str(uuid.uuid4())[:12],
        'market': model_meta.Market.CRYPTO,
        'name': str(uuid.uuid4())[:200],
        'company_id': company_from_db.id,
        'currency': model_meta.Currency.USD,
        'datafeed_src_id': datafeed_src_from_db.id,
    }
    _test_int__model_crud(pg_test_orm, security.Security, init_data, 'name')
    pg_test_orm._db._conn.close()
