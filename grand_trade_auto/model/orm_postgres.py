#!/usr/bin/env python3
"""
This defines the Object-Relational Mapping between the Models and the Postgres
database.

This implements the actual SQL needed for saving each Model, relying on the
table name and columns provided by those models.

Note that for table creation, the table name and columns are HARD CODED here,
effectively duplicating that information from the Models.  If these ever need to
change, this MUST be a coordinated change between the model and this ORM (and
some form of migration needs to be designed and done).

Goal of the ORM is to support what is needed to interface with the datafeeds and
other automated input data in a generic way.  It is NOT meant to encapsulate all
functionality that a strategy may want for manipulation, for example, as those
other uses are expected to directly use database invocation as needed.  In this
vein, joins are NOT supported at this time.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.model import orm_meta



class PostgresOrm(orm_meta.Orm):
    """
    The Object-Relational Mapping for Postgres.  Implements the SQL statements
    to create all tables as well as all CRUD operations for all Models.

    Class Attributes:
      N/A

    Instance Attributes:

      [inherited from Orm]:
        _db (Database): The database instance that this interfaces with.
    """



    def _create_schema_datafeed_src(self):
        """
        Create the datafeed_src table.

        Subclass must define and execute SQL/etc.
        """
        # TODO: Implement



    def add(self, model_cls, data):
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
        """
        # TODO: Implement



    def update(self, model_cls, data, where):
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
        """
        # TODO: Implement



    def delete(self, model_cls, where, really_delete_all=False):
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
        """
        # TODO: Implement



    def query(self, model_cls, return_as, columns_to_return=None,
            where=None, limit=None, order=None):
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

        Returns:
          If return_as == ReturnAs.MODEL:
            ([Model<>]): The list of model objects created from these results.
              Empty list if no matching results.
          If return_as == ReturnAs.PANDAS:
            (pandas.dataframe): The pandas dataframe representing all results.
        """
        # TODO: Implement
