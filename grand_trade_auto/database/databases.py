#!/usr/bin/env python3
"""
The database API module.  This is intended to be the item accessed outside of
the database submodule/folder.

Module Attributes:
  _DBMSS ((Class<Database<>>)): All database classes supported.
  _dbs_loaded ({str: Database<>}): The databases loaded and cached, keyed by
    their DB IDs (i.e. conf section IDs).

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.database import postgres
from grand_trade_auto.general import config



_DBMSS = (
    postgres.Postgres,
)

_dbs_loaded = {}



def get_database(db_id, env=None):
    """
    Gets the requested database.  Will return cached version if already
    loaded, otherwise will load and cache.

    Args:
      db_id (str): The section ID of the database from the databases.conf file.
      env (str or None): The environment for which this database is valid.
        Optional - can be used to be protect against incorrect access.

    Returns:
      db (Database<> or None): Returns the database that matches the given
        criteria, loading from conf if required.  None if no matching database.

    Raises:
      (AssertionError): Raised when an invalid combination of input arg
        criteria provided cannot guarantee a minimum level of definition.
    """
    assert db_id is not None

    if db_id in _dbs_loaded:
        if _dbs_loaded[db_id].matches_id_criteria(db_id, env):
            return _dbs_loaded[db_id]

    db = _get_database_from_config(db_id, env)
    if db is not None:
        _dbs_loaded[db_id] = db
    return db



def _get_database_from_config(db_id, env=None):
    """
    Loads the specified database from the config file.

    Arg:
      db_id (str): The section ID of the database from the databases.conf file
        to load.
      env (str or None): The environment for which this database is valid.
        Optional - can be used to be protect against incorrect access.

    Returns:
      db (Datbase<> or None): The database loaded and created from the config
        file based on the provided criteria.  None if no match found.

    Raises:
      (AssertionError): Raised if database cannot be loaded.
    """
    assert db_id is not None

    db_cp = config.read_conf_file('databases.conf')
    secrets_cp = config.read_conf_file('.secrets.conf')

    if db_id not in db_cp.sections():
        return None

    if env is not None and env != db_cp[db_id]['env'].strip():
        return None

    dbms_sel = None
    for dbms in _DBMSS:
        if db_cp[db_id]['dbms'].strip() in dbms.get_dbms_names():
            dbms_sel = dbms
            break

    if dbms_sel is None:
        return None

    secrets_id = config.get_matching_secrets_id(secrets_cp, 'database', db_id)
    db = dbms_sel.load_from_config(db_cp, db_id, secrets_id)
    return db
