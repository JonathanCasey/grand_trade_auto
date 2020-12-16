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



def load_databases_from_config(env):
    """
    Loads the databases from the config file and sets the first one it finds to
    be the valid one to use.  Stores for later access.

    Arg:
      env (str): The environment for which to load database config.

    Raises:
      (AssertionError): Raised if database already loaded or cannot be loaded.
    """
    global DB_HANDLE    # pylint: disable=global-statement
    assert DB_HANDLE is None, "Cannot load databases: Database already loaded."

    db_cp = config.read_conf_file('databases.conf')
    secrets_cp = config.read_conf_file('.secrets.conf')

    for db_id in db_cp.sections():
        if env != db_cp[db_id]['env']:
            continue

        secrets_id = None
        for secrets_section_name in secrets_cp:
            try:
                submod, sid = secrets_section_name.split('::')
                if submod.strip().lower() == 'database' \
                        and sid.strip().lower() == db_id.strip().lower():
                    secrets_id = secrets_section_name
            except ValueError:
                continue

        db_type = db_cp[db_id]['type'].strip()

        if db_type in database_postgres.DatabasePostgres.get_type_names():
            db_handle = database_postgres.DatabasePostgres.load_from_config(
                    db_cp, db_id, secrets_cp, secrets_id)

            if db_handle is not None:
                DB_HANDLE = db_handle
                break

    assert DB_HANDLE is not None, "No valid database configuration found."



if __name__ == '__main__':
    # TEMP: Just for initial dev tests until real tests written
    load_databases_from_config('development')
    print('Done')
