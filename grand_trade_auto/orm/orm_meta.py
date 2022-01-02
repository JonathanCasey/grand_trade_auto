#!/usr/bin/env python3
"""
This defines the generic interface required by all Object-Relational Mappings
(ORMs).  These will manage the translation between all models and each database.

This will be subclassed for each database class, and each of those subclasses
will need to support all models.  Subclasses will hold the actual SQL / etc
queries for their individual tied dbs.

Goal of the ORM is to support what is needed to interface with the datafeeds and
other automated input data in a generic way.  It is NOT meant to encapsulate all
functionality that a strategy may want for manipulation, for example, as those
other uses are expected to directly use database invocation as needed.  In this
vein, joins are NOT supported at this time.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from abc import ABC, abstractmethod



class NonexistentColumnError(Exception):
    """
    Raised when a column name is used in a database query that is not one of the
    column names defined in the Model's _column list.  This protects against SQL
    injection if specifying the column names is ever an externally facing user
    input.
    """



class Orm(ABC):
    """
    The Object-Relational Mapping skeleton structure.  Generic logic included
    here where any database-specific items being left to subclasses to define.

    Class Attributes:
      N/A

    Instance Attributes:
      _db (Database): The database instance that this interfaces with.
    """
    def __init__(self, db):
        """
        Creates the ORM.

        Args:
          db (Database): The database instance that this interfaces with.
        """
        self._db = db



    def create_schemas(self):
        """
        Create all schemas for the entire database.  Each ORM/database is
        expected to create the full database schema, even if not all of the
        tables will be loaded with data in this particular database.
        """
        self._create_schema_enum_currency()
        self._create_schema_enum_market()
        self._create_schema_enum_price_frequency()

        self._create_schema_table_datafeed_src()
        self._create_schema_table_exchange()
        self._create_schema_table_company()
        self._create_schema_table_security()
        self._create_schema_table_security_price()
        self._create_schema_table_stock_adjustment()



    @abstractmethod
    def _create_schema_enum_currency(self):
        """
        Create the currency enum.  The values must all match exactly the values as
        shown in model_meta.

        Dependent on: None
        Dependent on tables: N/A

        Subclass must define and execute SQL/etc.
        """



    @abstractmethod
    def _create_schema_enum_market(self):
        """
        Create the market enum.  The values must all match exactly the values as
        shown in model_meta.

        Dependent on: None
        Dependent on tables: N/A

        Subclass must define and execute SQL/etc.
        """



    @abstractmethod
    def _create_schema_enum_price_frequency(self):
        """
        Create the price_frequency enum.  The values must all match exactly the
        values as shown in model_meta.

        Dependent on: None
        Dependent on tables: N/A

        Subclass must define and execute SQL/etc.
        """



    @abstractmethod
    def _create_schema_table_company(self):
        """
        Create the company table.

        Dependent on enums: None
        Dependent on tables: datafeed_src

        Subclass must define and execute SQL/etc.
        """



    @abstractmethod
    def _create_schema_table_datafeed_src(self):
        """
        Create the datafeed_src table.

        Dependent on enums: None
        Dependent on tables: None

        Subclass must define and execute SQL/etc.
        """



    @abstractmethod
    def _create_schema_table_exchange(self):
        """
        Create the exchange table.

        Dependent on enums: None
        Dependent on tables: datafeed_src

        Subclass must define and execute SQL/etc.
        """



    @abstractmethod
    def _create_schema_table_security(self):
        """
        Create the security table.

        Dependent on enums: currency, market
        Dependent on tables: company, datafeed_src, exchange

        Subclass must define and execute SQL/etc.
        """



    @abstractmethod
    def _create_schema_table_security_price(self):
        """
        Create the security_price table.

        Dependent on enums: price_frequency
        Dependent on tables: datefeed_src, security

        Subclass must define and execute SQL/etc.
        """



    @abstractmethod
    def _create_schema_table_stock_adjustment(self):
        """
        Create the stock adjustment table.

        Dependent on enums: None
        Dependent on tables: datafeed_src, security

        Subclass must define and execute SQL/etc.
        """



    @abstractmethod
    def add(self, model_cls, data, **kwargs):
        """
        Adds/Inserts a new record into the database.  The table is acquired from
        the model class.  All necessary data must be provided (i.e. can omit
        columns that allow null).

        Subclass must define and execute SQL/etc.

        Args:
          model_cls (Class<Model<>>): The class itself of the model being added.
          data ({str:str/int/bool/datetime/enum/etc}): The data to be inserted,
            where the keys are the column names and the values are the
            python-type values to be inserted.
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Database.execute()`.  See those docstrings for more
            details.
        """



    @abstractmethod
    def update(self, model_cls, data, where, **kwargs):
        """
        Update record(s) in the database.  The table is acquired from the model
        class.

        Subclass must define and execute SQL/etc.

        Args:
          model_cls (Class<Model<>>): The class itself of the model being added.
          data ({str:str/int/bool/datetime/enum/etc}): The data to be updated,
            where the keys are the column names and the values are the
            python-type values to be used as the new values.
          where ({}/[]/() or None): The structured where clause.  See the
            Model.query_direct() docs for spec.  If None, will not filter.
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Database.execute()`.  See those docstrings for more
            details.
        """



    @abstractmethod
    def delete(self, model_cls, where, really_delete_all=False, **kwargs):
        """
        Delete record(s) in the database.  The table is acquired from the model
        class.

        Subclass must define and execute SQL/etc.

        Args:
          model_cls (Class<Model<>>): The class itself of the model being added.
          where ({}/[]/() or None): The structured where clause.  See the
            Model.query_direct() docs for spec.  If None, will not filter.
            WARNING: NOT providing a where clause will delete ALL data from the
            table.  This will not be done unless the `really_delete_all` is
            True.
          really_delete_all (bool): Confirms that all data should be deleted
            from the table.  Must be set to True AND the where clause must be
            None for this to happen.
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Database.execute()`.  See those docstrings for more
            details.
        """



    @abstractmethod
    def query(self, model_cls, return_as, columns_to_return=None,
            where=None, limit=None, order=None, **kwargs):
        """
        Query/Select record(s) from the database.  The table is acquired from
        the model class.  This gives a few options as far as how the data can be
        returned.  Some of the typical query options are included, but some like
        the where and order clauses have a structured input that must be used.

        Subclass must define and execute SQL/etc.

        Args:
          model_cls (Class<Model<>>): The class itself of the model being added.
          return_as (ReturnAs): Specifies which format to return the data in.
            Where possible, each format option is derived directly from the
            database cursor to optimize performance for all.
          columns_to_return ([str] or None): The columns to return from the
            table.  If None, will return all.
          where ({}/[]/() or None): The structured where clause.  See the
            Model.query_direct() docs for spec.  If None, will not filter.
          limit (int or None): The maximum number of records to return.  If
            None, will not impose a limit.
          order ([()]): The structured order clause.  See the
            Model.query_direct() docs for spec.  If None, will not impose order.
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Database.execute()`.  See those docstrings for more
            details.

        Returns:
          If return_as == ReturnAs.MODEL:
            ([Model<>]): The list of model objects created from these results.
              Empty list if no matching results.
          If return_as == ReturnAs.PANDAS:
            (pandas.dataframe): The pandas dataframe representing all results.
        """
