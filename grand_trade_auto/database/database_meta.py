#!/usr/bin/env python3
"""
Holds the generic database meta-class that others will subclass.  Any other
shared database code that needs to be accessed by all databases can be
implemented here so they have access when this is imported.

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from abc import ABC, abstractmethod



class DatabaseMeta(ABC):
    """
    The abstract class for all database functionality.  Each database type
    will subclass this, but externally will likely only call the generic methods
    defined here to unify the interface.

    Class Attributes:
      N/A

    Instance Attributes:
      N/A
    """
    @abstractmethod
    def __init__(self, host, port, database, username, password):
        """
        Creates the database handle.

        Args:
          host (str): The host URL.
          post (int): The port number on that host for accessing the database.
          database (str): The database to open.
          username (str): The username to use for logging in.
          password (str): The password to use for logging in.
        """



    @classmethod
    @abstractmethod
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
          db_handle (DatabaseMeta<>): The DatabaseMeta<> object created and
            loaded from config, where DatabaseMeta<> is a subclass of
            DatabaseMeta (e.g. DatabasePostgres).
        """



    @classmethod
    @abstractmethod
    def get_type_names(cls):
        """
        Get the list of names that can be used as the 'type' in the database
        conf to identify this database.

        Returns:
          ([str]): A list of names that are valid to use for this database type.
        """



    # @abstractmethod
    # def open_or_create_database(self):
    #     """
    #     """
    #     raise NotImplementedError
