#!/usr/bin/env python3
"""
Holds the generic database meta-class that others will subclass.  Any other
shared database code that needs to be accessed by all databases can be
implemented here so they have access when this is imported.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from abc import ABC, abstractmethod
import logging



logger = logging.getLogger(__name__)



class Database(ABC):
    """
    The abstract class for all database functionality.  Each database type
    will subclass this, but externally will likely only call the generic methods
    defined here to unify the interface.

    This serves as a base class for other database systems, so will consume
    any final kwargs.

    Class Attributes:
      N/A

    Instance Attributes:
      _env (str): The run environment type valid for using this database.
      _db_id (str): The id used as the section name in the database conf.
      _orm (Orm<>): The ORM for this database subclass.
    """
    _orm = None     # Subclass instance MUST override this value



    def __init__(self, env, db_id, **kwargs):
        """
        Creates the database handle.

        Subclasses are expected to initialize their own Orm.

        Args:
          env (str): The run environment type valid for using this database.
          db_id (str): The id used as the section name in the database conf.
        """
        self._env = env
        self._db_id = db_id

        if kwargs:
            logger.warning('Discarded excess kwargs provided to'
                    + f' {self.__class__.__name__}: {", ".join(kwargs.keys())}')



    @property
    def orm(self):
        """
        Gets the Orm for this database in a read-only fashion.  Subclasses must
        override with to return their actual Orm.
        """
        return self._orm



    def matches_id_criteria(self, db_id, env=None, dbms=None):
        """
        Checks if this database is a match based on the provided criteria.

        Can provide more beyond minimum required parameters to explicitly
        overdefine.  No matter how minimally or overly defined inputs are, all
        non-None must match.

        Args:
          db_id (str): The section ID of the database from the databases.conf
            file to check if this matches.
          env (str or None): The environment for which to check if this matches.
          dbms (str or None): The DBMS type to check if this matches.


        Returns:
          (bool): True if all provided criteria match; False otherwise.

        Raises:
          (AssertionError): Raised when an invalid combination of input arg
            criteria provided cannot guarantee a minimum level of definition.
        """
        assert db_id is not None
        if db_id != self._db_id:
            return False
        if env is not None and env != self._env:
            return False
        if dbms is not None and dbms not in self.get_dbms_names():
            return False
        return True



    @classmethod
    @abstractmethod
    def load_from_config(cls, db_cp, db_id):
        """
        Loads the database config for this database from the configparsers
        from files provided.

        Args:
          db_cp (configparser): The full configparser from the database conf.
          db_id (str): The ID name for this database as it appears as the
            section header in the db_cp.

        Returns:
          db (Database<>): The Database<> object created and loaded from
            config, where Database<> is a subclass of Database (e.g. Postgres).
        """



    @classmethod
    @abstractmethod
    def get_dbms_names(cls):
        """
        Get the list of names that can be used as the 'dbms' in the database
        conf to identify this database management system type.

        Returns:
          ([str]): A list of names that are valid to use for this DataBase
            Management System.
        """



    def connect(self, cache=True):
        """
        """



    @abstractmethod
    def create_db(self):
        """
        Creates the database specified as the database to use in this object.
        If it already exists, skips.
        """



    @abstractmethod
    def cursor(self):
        """
        """



    @abstractmethod
    def execute(self, command, val_vars=None, cursor=None, commit=True,
            close_cursor=True):
        """
        """
