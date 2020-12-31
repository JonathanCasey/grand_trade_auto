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
      host (str): The host URL.
      post (int): The port number on that host for accessing the database.
      database (str): The database to open.
      cp_db_id (str): The id used as the section name in the database conf.
        Will be used for loading credentials on-demand.
      cp_secrets_id (str): The id used as the section name in the secrets
        conf.  Will be used for loading credentials on-demand.
    """
    @abstractmethod
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



    @classmethod
    @abstractmethod
    def load_from_config(cls, db_cp, db_id, secrets_id):
        """
        Loads the database config for this database from the configparsers
        from files provided.

        Args:
          db_cp (configparser): The full configparser from the database conf.
          db_id (str): The ID name for this database as it appears as the
            section header in the db_cp.
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



    @abstractmethod
    def create_db(self):
        """
        Creates the database specified as the database to use in this object.
        If it already exists, skips.
        """
