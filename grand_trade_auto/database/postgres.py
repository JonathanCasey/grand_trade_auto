#!/usr/bin/env python3
"""
PostgreSQL functionality to implement the generic interface components defined
by the metaclass.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from psycopg2 import sql
import psycopg2

from grand_trade_auto.database import database_meta
from grand_trade_auto.general import config
from grand_trade_auto.model import orm_postgres



logger = logging.getLogger(__name__)



class Postgres(database_meta.Database):
    """
    The PostgreSQL database functionality.

    Class Attributes:
      N/A

    Instance Attributes:
      _host (str): The host URL.
      _post (int): The port number on that host for accessing the database.
      _database (str): The database to open.
      _user (str): The user to use for authentication.
      _password (str): The password to use for authentication.

      _conn (connection): The cached database connection; or None if not
        connected and cached.

      [inherited from Database]:
        _env (str): The run environment type valid for using this database.
        _db_id (str): The id used as the section name in the database conf.
        _orm (PostgresOrm): The ORM for this database subclass.
    """
    def __init__(self, host, port, database, user, password, **kwargs):
        """
        Creates the database handle.

        Subclasses are expected to initialize their own Orm.

        Args:
          host (str): The host URL.
          post (int): The port number on that host for accessing the database.
          database (str): The database to open.
          user (str): The user to use for authentication.
          password (str): The password to use for authentication.

          See parent(s) for required kwargs.
        """
        super().__init__(**kwargs)
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

        self._conn = None

        self._orm = orm_postgres.PostgresOrm(self)



    @classmethod
    def load_from_config(cls, db_cp, db_id):
        """
        Loads the database config for this database from the configparsers
        from files provided.

        Args:
          db_cp (configparser): The full configparser from the database conf.
          db_id (str): The ID name for this database as it appears as the
            section header in the db_cp.

        Returns:
          db (Postgres): The Postgres object created and loaded from config
            based on the provided config data.
        """
        db_cp = config.read_conf_file('databases.conf')
        secrets_cp = config.read_conf_file('.secrets.conf')
        secrets_id = config.get_matching_secrets_id(secrets_cp, 'database',
                db_id)

        kwargs = {}
        kwargs['env'] = db_cp[db_id]['env']
        kwargs['db_id'] = db_id
        kwargs['host'] = db_cp[db_id]['host url']
        kwargs['database'] = db_cp[db_id]['database']
        kwargs['port'] = db_cp.getint(db_id, 'port', fallback=5432)

        kwargs['user'] = db_cp.get(db_id, 'username', fallback=None)
        kwargs['user'] = secrets_cp.get(secrets_id, 'username',
                fallback=kwargs['user'])
        kwargs['password'] = secrets_cp.get(secrets_id, 'password',
                fallback=None)

        db = Postgres(**kwargs)
        return db



    @classmethod
    def get_dbms_names(cls):
        """
        Get the list of names that can be used as the 'dbms' in the database
        conf to identify this database management system type.

        Returns:
          ([str]): A list of names that are valid to use for this DataBase
            Management System.
        """
        return ['postgres', 'postgresql']



    def connect(self, cache=True, database=None):
        """
        Connect to PostgreSQL.  The database can be overridden, which is useful
        when a default database is needed for initial connections.

        Args:
          cache (bool): Whether to use the existing connection and store it if
            created; False will force a new connection that will not be saved.
          database (str or None): The name of the database to conenct.  If None
            provided, will use the database name stored in this object.

        Returns:
          (connection): The cached connection if specified and existed;
            otherwise new database connection established.
        """
        if cache and self._conn is not None:
            return self._conn

        kwargs = {
            'host': self._host,
            'port': self._port,
            'user': self._user,
            'password': self._password,
        }
        if database is None:
            database = self._database
        kwargs['database'] = database

        conn = psycopg2.connect(**kwargs)
        if cache:
            self._conn = conn
            logger.info('Connected to'        # pylint: disable=logging-not-lazy
                    + f' database \'{database}\' successfully and cached.')
        else:
            logger.info(f'Connected to database \'{database}\' successfully.')
        return conn



    def _check_if_db_exists(self):
        """
        Checks if the database specified as the database to use in this object
        already exists.

        Returns:
          (bool): True if it already exists; False otherwise.
        """
        # Since expectation db may not exist, support conn to default db
        if self._conn is None or self._conn.closed:
            conn = self.connect(False, 'postgres')
        else:
            conn = self._conn

        cursor = conn.cursor()
        sql_check_db = 'SELECT 1 FROM pg_database WHERE datname=%(database)s'
        cursor.execute(sql_check_db, {'database': self._database})
        result = cursor.fetchone()

        exists = False
        if result is not None and result[0] == 1:
            exists = True

        cursor.close()
        if conn != self._conn:
            conn.close()

        return exists



    def create_db(self):
        """
        Creates the database specified as the database to use in this object.
        If it already exists, skips.
        """
        if self._check_if_db_exists():
            return

        conn = self.connect(False, 'postgres')
        conn.autocommit = True
        cursor = conn.cursor()
        sql_create_db = sql.SQL('CREATE DATABASE {database};').format(
                database=sql.Identifier(self._database))
        cursor.execute(sql_create_db)
        logger.info(f'Database \'{self._database}\' created successfully.')
        cursor.close()
        conn.close()



    def _drop_db(self):
        """
        This drops the database specified as the database to use in this object.

        WARNING: THIS IS A DESTRUCTIVE ACTION!!

        This primarily exists for testing and setup purposes; it is extremely
        unlikely it should be called in main, normal functioning of the app.
        """
        # Use fresh connection so can use autocommit without caring about
        #   restoring state; and not expected to be used frequently.
        conn = self.connect(False, 'postgres')
        conn.autocommit = True
        cursor = conn.cursor()
        sql_drop_db = sql.SQL('DROP DATABASE IF EXISTS {database};').format(
                    database=sql.Identifier(self._database))
        logger.warning(f'Database \'{self._database}\' dropped!')
        cursor.execute(sql_drop_db)
        cursor.close()
        conn.close()
