"""
The database API module.  This is intended to be the item accessed outside of
the database submodule/folder.

Module Attributes:
  DB_HANDLE (DatabaseMeta<>): The handle to the database that will be used,
    where DatabaseMeta<> is a subclass of DatabaseMeta (e.g. DatabasePostgres).

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.database import database_postgres
from grand_trade_auto.general import config



DB_HANDLE = None



def load_and_set_main_database_from_config(env, db_type=None):
    """
    Loads the main database from config and sets it as the main handle open.

    Arg:
      env (str): The environment for which to load database config.
      db_type (str or None): The database type to be forced as the one to load;
        or None to simply take the first one found.

    Raises:
      (AssertionError): Raised if database already loaded or cannot be loaded.
    """
    global DB_HANDLE    # pylint: disable=global-statement
    assert DB_HANDLE is None, "Cannot load databases: Database already loaded."
    db_handle = get_database_from_config(env, db_type)
    if db_handle is not None:
        DB_HANDLE = db_handle
    assert DB_HANDLE is not None, "No valid database configuration found."



def get_database_from_config(env, db_type=None):
    """
    Loads the databases from the config file and sets the first one it finds to
    be the valid one to use.  Stores for later access.

    Arg:
      env (str): The environment for which to load database config.
      db_type (str or None): The database type to be forced as the one to load;
        or None to simply take the first one found.

    Raises:
      (AssertionError): Raised if database already loaded or cannot be loaded.
    """
    db_cp = config.read_conf_file('databases.conf')
    secrets_cp = config.read_conf_file('.secrets.conf')

    for db_id in db_cp.sections():
        if env != db_cp[db_id]['env'].strip():
            continue

        secrets_id = config.get_matching_secrets_id(secrets_cp, 'database',
                db_id)

        postgres_type_names = \
                database_postgres.DatabasePostgres.get_type_names()
        if db_cp[db_id]['type'].strip() in postgres_type_names:
            if db_type is not None and db_type not in postgres_type_names:
                continue

            db_handle = database_postgres.DatabasePostgres.load_from_config(
                    db_cp, db_id, secrets_cp, secrets_id)

            if db_handle is not None:
                return db_handle
    return None
