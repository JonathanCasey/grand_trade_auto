"""
PostgreSQL functionality to implement the generic interface components defined
by the metaclass.

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import psycopg2

from grand_trade_auto.database import database_meta
from grand_trade_auto.general import config



class DatabasePostgres(database_meta.DatabaseMeta):
    """
    The PostgreSQL database functionality.

    Class Attributes:
      N/A

    Instance Attributes:
      host (str): The host URL.
      post (int): The port number on that host for accessing the database.
      database (str): The database to open.
      cp_db_id (str): The id used as the section name in the database conf.
        Will be used for loading credentials on-demand.
      cp_secrets_id (str): The id used as the section name in the secrets
        conf.  Will be used for loading credentials on-demand.
    """
    def __init__(self, host, port, database, cp_db_id, cp_secrets_id):
        """
        Creates the database handle.

        Args:
          host (str): The host URL.
          post (int): The port number on that host for accessing the database.
          database (str): The database to open.
          cp_db_id (str): The id used as the section name in the database conf.
            Will be used for loading credentials on-demand.
          cp_secrets_id (str): The id used as the section name in the secrets
            conf.  Will be used for loading credentials on-demand.
        """
        self.host = host
        self.port = port
        self.database = database
        self.cp_db_id = cp_db_id
        self.cp_secrets_id = cp_secrets_id
        super().__init__(host, port, database, cp_db_id, cp_secrets_id)

        self.conn = None



    @classmethod
    def load_from_config(cls, db_cp, db_id, secrets_cp, secrets_id):
        """
        Loads the database config for this database from the configparsers
        from files provided.

        Args:
          db_cp (configparser): The full configparser from the database conf.
          db_id (str): The ID name for this database as it appears as the
            section header in the db_cp.
          secrets_cp (configparser): The full configparser from the secrets
            conf.
          secrets_id (str): The ID name for this database's secrets as it
            appears as the section header in the secrets_cp.

        Returns:
          db_handle (DatabasePostgres): The DatabasePostgres object created and
            loaded from config based on the provided config data.
        """
        kwargs = {}

        kwargs['host'] = db_cp[db_id]['host url']
        kwargs['database'] = db_cp[db_id]['database']
        kwargs['port'] = db_cp.getint(db_id, 'port', fallback=5432)
        kwargs['cp_db_id'] = db_id
        kwargs['cp_secrets_id'] = secrets_id

        db_handle = DatabasePostgres(**kwargs)
        return db_handle



    @classmethod
    def get_type_names(cls):
        """
        Get the list of names that can be used as the 'type' in the database
        conf to identify this database.

        Returns:
          ([str]): A list of names that are valid to use for this database type.
        """
        return ['postgres', 'postgresql']



    def connect(self, database=None):
        """
        Connect to PostgreSQL.  The database can be overridden, which is useful
        when a default database is needed for initial connections.

        Args:
          database (str or None): The name of the database to conenct.  If None
            provided, will use the database name stored in this object.

        Returns:
          (connection): The new database connection established.
        """
        db_cp = config.read_conf_file('databases.conf')
        secrets_cp = config.read_conf_file('.secrets.conf')

        kwargs = {
            'host': self.host,
            'port': self.port,
        }
        if database is not None:
            kwargs['database'] = database
        else:
            kwargs['database'] = self.database

        kwargs['user'] = db_cp.get(self.cp_db_id, 'username',
                fallback=None)
        kwargs['password'] = secrets_cp.get(self.cp_secrets_id, 'password',
                fallback=None)
        kwargs['user'] = secrets_cp.get(self.cp_secrets_id, 'username',
                fallback=kwargs['user'])

        return psycopg2.connect(**kwargs)



    # def open_or_create_database(self):
    #     """

    #     """
