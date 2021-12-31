#!/usr/bin/env python3
"""
This defines the generic interface that all data models must implement, as well
as any constants used by all (e.g. all enums used in dbs).  This is intended to
be used with subclasses of Orm for genericized database access.

This will be subclassed for each data model.  For the most part, these will only
need to define the table name and also the columns, both as a list of strings
and as attributes.

This will provide a generic interface for datafeeds and other automated input.
It can also be used for simple manipulation, but is not intended to be fully
encompassing, nor fully execution optimized.  See the Orm module doc string for
more details on the limitations of its goal.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from abc import ABC
from enum import Enum
import logging



logger = logging.getLogger(__name__)



class ReturnAs(Enum):
    """
    Options for how query results can be returned.  In some places, can use
    value directly, but there may be a performance cost.
    """
    MODEL = 'model'
    PANDAS = 'pandas'



class LogicOp(Enum):
    """
    The logic operators that can be used in reference to a column and a possible
    value in a where subclause.  See the Model.query_direct() for more details
    on the structure of this where clause.  Intended to use as enum, not as
    value directly due to performance hit to support both.

    EQUAL and EQUALS can be used interchangeably.  This was originally intended
    to allow interchangeable support for single and double equal signs.

    All others that looks to be using the same symbol are intended to be
    equivalent shortcuts.
    """
    EQUAL = '=='
    EQUALS = '='
    EQ = '= '

    LESS_THAN = '<'
    LT = '< '

    LESS_THAN_OR_EQUAL = '<='
    LTE = '<= '

    GREATER_THAN = '>'
    GT = '> '

    GREATER_THAN_OR_EQUAL = '>='
    GTE = '>= '

    NOT_NULL = 'not null'



class LogicCombo(Enum):
    """
    The logic combiners/conjunctions that can be used to specify how a multitude
    of subclauses are to be combined at a given level.  See the
    Model.query_direct() for more details on the structure of this where clause.
    Intended to use as enum, not as value directly due to performance hit to
    support both.
    """
    AND = 'and'
    OR = 'or'



class SortOrder(Enum):
    """
    The options for sort order to be used in combination with a column for an
    individual sort subclause.  See Model.query_direct() for more details on the
    structure of this order clause.  Intended to use as enum, not as value
    directly due to performance hit to support both.
    """
    ASC = 'asc'
    DESC = 'desc'



class Model(ABC):
    """
    The generic data model.  This encapsulate almost all the functionality to be
    used by all models in a generic way so that, for the most part, the
    subclasses will only need to define the table name and the columns as a list
    of strings and as attributes.

    Class Attributes:
      _table_name (str or None): The name of the table in the database.
        Subclasses should override and then never change...
      _columns ([str] or None): The list of column names in the table.  These
        should each have a class attribute with a matching name for ease of
        access.  Subclasses should override this with the name of columns and
        then never change...
      id (int or None): [Column var] The value of the id column in the table
        for this record.  All tables MUST have an id field, at least until
        some TSDB shows up.  As a class attribute, this is intended to hold
        some default value.  It will be superseded its corresponding instance
        variable upon being written to.  This is the practice for all
        column-related attributes.

    Instance Attributes:
      _orm (Orm): The ORM that is being used to interact with the
        database for this model.
      _active_cols (set(str)): The columns that are "active" in this record.
        This will essentially exclude any columns that were not pulled from the
        database nor were written to here so that, in the event of an update,
        only the columns populated here will be updated.  Subclasses should not
        need to touch this.
    """
    _table_name = None
    _columns = None

    # Column Attributes -- MUST match _columns!
    id = None
    # End of Column Attributes



    def __init__(self, orm, data=None):
        """
        Creates the model.  Subclasses should not need to override unless doing
        something extra special.

        Args:
          orm (Orm): The ORM that is being used to interact with the database
            for this model.
          data ({str:str/int/bool/datetime/enum/etc}): The data defining this
            model's initial values, where the keys are the column names and the
            values are the python-type values.  Can be None or empty to get a
            blank record (e.g. to add a new record).
        """
        self._orm = orm
        self._active_cols = set()

        if data is not None:
            for k, v in data.items():
                assert k in self._columns, f'Invalid data column: {k}'
                self.__setattr__(k, v)



    def __setattr__(self, name, value):
        """
        Sets an instance attribute with the given name to the given value.

        This is only slightly modified to also mark active columns, but
        otherwise still falls through to normal behavior (including for active
        columns).

        name (str): The name of the instance attribute to update.
        value (any): The value to set that instance attribute to.
        """
        if name in self._columns:
            self._active_cols.add(name)
        return super().__setattr__(name, value)



    @classmethod
    def get_table_name(cls):
        """
        Get the table name for this model.

        Returns:
          _table_name (str): The table name.
        """
        return cls._table_name



    @classmethod
    def get_columns(cls):
        """
        Gets the list of column names for this model.

        Returns:
          _columns ([str]): The list of column names.
        """
        return cls._columns



    @classmethod
    def add_direct(cls, orm, data, **kwargs):
        """
        Add/Insert a new record for this data model.  This will NOT create a
        model object first, but rather will directly route the data to the ORM
        for better optimization.

        Args:
          orm (Orm): The ORM to use for this database interaction.
          data ({str:str/int/bool/datetime/enum/etc}): The data to be inserted,
            where the keys are the column names and the values are the
            python-type values to be inserted.
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Orm.add()`.  See those docstrings for more details.
        """
        orm.add(cls, data, **kwargs)



    @classmethod
    def update_direct(cls, orm, data, where, **kwargs):
        """
        Update an existing record for this data model.  This will NOT create a
        model object first, but rather will directly route the data to the ORM
        for better optimization.

        Args:
          orm (Orm): The ORM to use for this database interaction.
          data ({str:str/int/bool/datetime/enum/etc}): The data to be updated,
            where the keys are the column names and the values are the
            python-type values to be used as the new values.
          where ({}/[]/() or None): The structured where clause.  See the
            Model.query_direct() docs for spec.  If None, will not filter.
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Orm.update()`.  See those docstrings for more details.
        """
        orm.update(cls, data, where, **kwargs)



    @classmethod
    def delete_direct(cls, orm, where, **kwargs):
        """
        Delete an existing record for this data model.  This will NOT create a
        model object first, but rather will directly route the data to the ORM
        for better optimization.

        Args:
          orm (Orm): The ORM to use for this database interaction.
          data ({str:str/int/bool/datetime/enum/etc}): The data to be updated,
            where the keys are the column names and the values are the
            python-type values to be used as the new values.
          where ({}/[]/() or None): The structured where clause.  See the
            Model.query_direct() docs for spec.  If None, will not filter.
            WARNING: NOT providing a where clause would translate to deleting
            ALL data from the table.  This is protected, however, by the ORM
            (assuming there are no bugs...).
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Orm.delete()`.  See those docstrings for more details.
        """
        orm.delete(cls, where, **kwargs)



    @classmethod
    def query_direct(cls, orm, return_as=ReturnAs.MODEL, columns_to_return=None,
            where=None, limit=None, order=None, **kwargs):
        """
        Query/Select record(s) from the database.  This gives a few options as
        far as how the data can be returned.  Some of the typical query options
        are included, but some like the where and order clauses have a
        structured input that must be used.


        __ where clause structure __

        The full where clause supports nesting and combinatorial logic for
        various types of conditionals.

        To start, a conditional statement is defined as a tuple/list that
        comprises a column name, a logic operator, and possible a value.  For
        example, to compare the id column equaling 1, the code would be:
        ```
        ('id', LogicOp.EQUALS, 1)
        ```

        If multiple conditionals are to be combined, these are defined as a
        single element dict, where the key specifies how they will all be
        combined and the dict's value is the tuple/list of conditionals.  For
        example, to compare the id column being greater than 1 and less than 5:
        ```
        {
            LogicCombo.AND: [
                ('id', LogicOp.GREATER_THAN, 1),
                ('id', LogicOp.LESS_THAN, 5),
            ],
        }
        ```

        Within the list of conditionals, any number of those can also be further
        combinations, nesting as deep as needed.  For a most complex example,
        to compare the id column being less than or equal to 123 and having a
        name of (Bob or Alice) and address is not null:
        ```
        {
            LogicCombo.AND: [
                ('id', LogicOp.LESS_THAN_OR_EQUAL, 123),
                LogicCombo.OR: [
                    ('name', LogicOp.EQUAL, 'Bob'),
                    ('name', LogicOp.EQUAL, 'Alice'),
                ],
                ('address', LogicOp.NOT_NULL),
            ],
        }
        ```

        As can be seen, `NOT_NULL` does not require a value at the end (it will
        be ignored).

        Note that this does mean that if there is only one conditional, the
        where clause is provided as a single tuple/list whereas in all
        combinatorial cases the outermost element is a dict.  This is the
        expected use and it will be handled by the ORM processor.


        __ order clause structure __

        The order clause allows the column and order to be provided, where
        multiple can be combined for subsorts.

        A single order clause is only a column name and a sort order:
        ```
        [
            ('id', SortOrder.ASC),
        ]
        ```

        Note that even with only a single sort condition, it is still wrapped in
        a list.  With multiple, the list is continued, but the order of the list
        is important, as sorts will be applied in the order in which they appear
        in the list.  So, for example, to sort by last name in Desc order then
        by first name in Desc order:
        ```
        [
            ('last_name', SortOrder.DESC),
            ('first_name', SortOrder.ASC),
        ]
        ```


        Args:
          orm (Orm): The ORM to use for this database interaction.
          return_as (ReturnAs): Specifies which format to return the data in.
            Where possible, each format option is derived directly from the
            database cursor to optimize performance for all.
          columns_to_return ([str] or None): The columns to return from the
            table.  If None, will return all.
          where ({}/[]/() or None): The structured where clause.  See for spec.
            If None, will not filter.
          limit (int or None): The maximum number of records to return.  If
            None, will not impose a limit.
          order ([()]): The structured order clause.  See above for spec.  If
            None, will not impose order.
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Orm.query()`.  See those docstrings for more details.

        Returns:
          If return_as == ReturnAs.MODEL:
            ([Model<>]): The list of model objects created from these results.
              Empty list if no matching results.
          If return_as == ReturnAs.PANDAS:
            (pandas.dataframe): The pandas dataframe representing all results.
        """
        return orm.query(cls, return_as, columns_to_return, where, limit, order,
                **kwargs)



    def add(self, **kwargs):
        """
        Add/Insert this model as a new record.

        Args:
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Orm.add()`.  See those docstrings for more details.
        """
        self.add_direct(self._orm, self._get_active_data_as_dict(), **kwargs)



    def update(self, **kwargs):
        """
        Update this model's record in the database.

        Args:
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Orm.update()`.  See those docstrings for more details.
        """
        self.update_direct(self._orm, self._get_active_data_as_dict(),
                self._get_where_self_id(), **kwargs)



    def delete(self, **kwargs):
        """
        Delete this model's record from the database.

        Args:
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Orm.delete()`.  See those docstrings for more details.
        """
        self.delete_direct(self._orm, self._get_where_self_id(), **kwargs)



    def _get_active_data_as_dict(self):
        """
        Takes the active data columns only to generate a dict of column:value
        pairs for database entry.

        Returns:
          ({str:str/int/bool/datetime/enum/etc}): The active data in this model.
        """
        return {c: getattr(self, c) for c in self._active_cols}



    def _get_where_self_id(self):
        """
        Compiles the full where clause when only trying to match its own record.

        Returns:
          ((str, LogicOp, int)): The tuple that represents the full structured
            where clause to identify this model's own record in the database
            table.
        """
        if self.id is None:
            err_msg = 'Cannot generate where clause with ID being None'
            logger.error(err_msg)
            raise ValueError(err_msg)
        return ('id', LogicOp.EQUALS, self.id)
