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
  _SCHEMA_NAME (str): The name of the schema in which all of this exists in the
    database.  This is likely the default value and is just there to ensure unit
    tests will always match what is used here.
  _TYPE_NAMESPACE (str): The name of the type namespace in which all the types
    exist in the databse for this project.  This is likely the default value and
    is just there to ensure unit tests will always match what is used there.
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging
from string import Template

import pandas as pd
import psycopg2.extensions

from grand_trade_auto.model import model_meta
from grand_trade_auto.orm import orm_meta



_SCHEMA_NAME = 'public' # Relying on 'public' being the default in psql
_TYPE_NAMESPACE = 'public'  # Relying on 'public' being the default in psql

logger = logging.getLogger(__name__)



class PostgresOrm(orm_meta.Orm):
    """
    The Object-Relational Mapping for Postgres.  Implements the SQL statements
    to create all tables as well as all CRUD operations for all Models.

    Class Attributes:
      _sql_exec_if_type_not_exists (string.Template): A wrapper for executing a
        SQL command only if a type does not exist within a given namespace.
        Since this is using template substitution rather than any kind of
        sanitized input, this is intended for internal use ONLY, and NOT for any
        external user input!
      _sql_select_type_oid (str): A SQL statement to get the OID for a type in a
        given namespace, with parameterization of the name and namespace.

    Instance Attributes:
      [inherited from Orm]:
        _db (Database): The database instance that this interfaces with.
    """
    _sql_exec_if_type_not_exists = Template('''
        DO $$$$ BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_type t
                    LEFT JOIN pg_namespace p ON t.typnamespace=p.oid
                WHERE t.typname='$type_name'
                    AND p.nspname='$type_namespace'
            ) THEN
                $sql_exec_if_not_exists;
            END IF;
        END $$$$;
    ''')
    _sql_select_type_oid = '''
        SELECT t.oid
        FROM pg_type t
            LEFT JOIN pg_namespace p ON t.typnamespace=p.oid
        WHERE t.typname=%(type_name)s
            AND p.nspname=%(type_namespace)s
    '''



    def _create_and_register_type_enum(self, enum_cls, enum_name, sql_create):
        """
        Creates and then registers a new enum type for bidirection conversion
        between python and PostgreSQL.

        Args:
          enum_cls (Class<Enum>): Reference to the enum class in python for
            which to add and register.
          enum_name (str): The name of the enum as it will appear in the
            database as a type name.
          sql_create (str): The SQL statement to execute to create the type.
            This does NOT need to include anything to check if the type exists,
            as that will be addressed here.
        """
        sql = self._sql_exec_if_type_not_exists.substitute(type_name=enum_name,
                type_namespace=_TYPE_NAMESPACE,
                sql_exec_if_not_exists=sql_create)
        self._db.execute(sql)


        def adapt_enum(enum_item):
            """
            Adapts a python enum type to a database value.

            Args:
              enum_item (enum_cls): The python enum item to convert.

            Returns:
              (ISLQuote): A SQL adaptation of the provided enum item.
            """
            return psycopg2.extensions.adapt(enum_cls(enum_item).value)

        psycopg2.extensions.register_adapter(enum_cls, adapt_enum)


        cursor = self._db.execute(self._sql_select_type_oid,
                {'type_name': enum_name, 'type_namespace': _TYPE_NAMESPACE},
                close_cursor=False)
        assert cursor.rowcount == 1 # Sanity check
        oid = cursor.fetchone()[0]
        cursor.close()

        def cast_enum(value, cursor):           #pylint: disable=unused-argument
            """
            Casts a database value to the python enum type.

            Args:
              value (?): The value retrieved from the database.
              cursor (cursor): The database cursor that retrieved the data.

            Returns:
              (enum_cls): An python enum of the specified Enum class.
            """
            return enum_cls(value)

        pgtype_enum = psycopg2.extensions.new_type((oid,), enum_name, cast_enum)
        psycopg2.extensions.register_type(pgtype_enum)



    def _create_schema_enum_currency(self):
        """
        Create the currency enum.  The values must all match exactly the values as
        shown in model_meta.

        Dependent on: None
        Dependent on tables: N/A

        Subclass must define and execute SQL/etc.
        """
        enum_name = 'currency'
        sql_create = f'''
            CREATE TYPE {enum_name} AS ENUM (
                'usd'
            )
        '''
        self._create_and_register_type_enum(model_meta.Currency,
                enum_name, sql_create)



    def _create_schema_enum_market(self):
        """
        Create the market enum.  The values must all match exactly the values as
        shown in model_meta.

        Dependent on: None
        Dependent on tables: N/A

        Subclass must define and execute SQL/etc.
        """
        enum_name = 'market'
        sql_create = f'''
            CREATE TYPE {enum_name} AS ENUM (
                'crypto', 'forex', 'futures', 'stock'
            )
        '''
        self._create_and_register_type_enum(model_meta.Market,
                enum_name, sql_create)



    def _create_schema_enum_price_frequency(self):
        """
        Create the price_frequency enum.  The values must all match exactly the
        values as shown in model_meta.

        Dependent on: None
        Dependent on tables: N/A

        Subclass must define and execute SQL/etc.
        """
        enum_name = 'price_frequency'
        sql_create = f'''
            CREATE TYPE {enum_name} AS ENUM (
                '1min', '5min', '10min', '15min', '30min', 'hourly', 'daily'
            )
        '''
        self._create_and_register_type_enum(model_meta.PriceFrequency,
                enum_name, sql_create)



    def _create_schema_table_company(self):
        """
        Create the company table.

        Dependent on enums: None
        Dependent on tables: datafeed_src

        Subclass must define and execute SQL/etc.
        """
        sql = '''
            CREATE TABLE IF NOT EXISTS company (
                id integer NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name varchar(50) NOT NULL,
                sector varchar(50),
                industry_group varchar(50),
                industry_category varchar(50),
                cik varchar(10),
                sic varchar(4),
                datafeed_src_id integer NOT NULL,
                CONSTRAINT fk_datafeed_src
                    FOREIGN KEY (datafeed_src_id)
                    REFERENCES datafeed_src (id)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE
            )
        '''
        self._db.execute(sql)



    def _create_schema_table_datafeed_src(self):
        """
        Create the datafeed_src table.

        Dependent on enums: None
        Dependent on tables: None

        Subclass must define and execute SQL/etc.
        """
        sql = '''
            CREATE TABLE IF NOT EXISTS datafeed_src (
                id integer NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                config_parser text NOT NULL,
                is_init_complete boolean,
                progress_marker text,
                UNIQUE (config_parser)
            )
        '''
        self._db.execute(sql)



    def _create_schema_table_exchange(self):
        """
        Create the exchange table.

        Dependent on enums: None
        Dependent on tables: datafeed_src

        Subclass must define and execute SQL/etc.
        """
        sql = '''
            CREATE TABLE IF NOT EXISTS exchange (
                id integer NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                name varchar(50) NOT NULL,
                acronym varchar(50) NOT NULL,
                datafeed_src_id integer NOT NULL,
                CONSTRAINT fk_datafeed_src
                    FOREIGN KEY (datafeed_src_id)
                    REFERENCES datafeed_src (id)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE,
                UNIQUE (name)
            )
        '''
        self._db.execute(sql)



    def _create_schema_table_security(self):
        """
        Create the security table.

        Dependent on enums: currency, market
        Dependent on tables: company, datafeed_src, exchange

        Subclass must define and execute SQL/etc.
        """
        sql = '''
            CREATE TABLE IF NOT EXISTS security (
                id integer NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                exchange_id integer NOT NULL,
                CONSTRAINT fk_exchange
                    FOREIGN KEY (exchange_id)
                    REFERENCES exchange (id)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE,
                ticker varchar(12) NOT NULL,
                market market NOT NULL,
                name varchar(200) NOT NULL,
                company_id integer NOT NULL,
                CONSTRAINT fk_company
                    FOREIGN KEY (company_id)
                    REFERENCES company (id)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE,
                currency currency NOT NULL,
                datafeed_src_id integer NOT NULL,
                CONSTRAINT fk_datafeed_src
                    FOREIGN KEY (datafeed_src_id)
                    REFERENCES datafeed_src (id)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE,
                UNIQUE (exchange_id, ticker)
            )
        '''
        self._db.execute(sql)



    def _create_schema_table_security_price(self):
        """
        Create the security_price table.

        Dependent on enums: price_frequency
        Dependent on tables: datefeed_src, security

        Subclass must define and execute SQL/etc.
        """
        sql = '''
            CREATE TABLE IF NOT EXISTS security_price (
                id bigint NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                security_id integer NOT NULL,
                CONSTRAINT fk_security
                    FOREIGN KEY (security_id)
                    REFERENCES security (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                datetime timestamptz NOT NULL,
                raw_open double precision,
                raw_close double precision,
                raw_high double precision,
                raw_low double precision,
                raw_volume double precision,
                adj_open double precision,
                adj_close double precision,
                adj_high double precision,
                adj_low double precision,
                adj_volume double precision,
                is_intraperiod boolean NOT NULL,
                frequency price_frequency NOT NULL,
                datafeed_src_id integer NOT NULL,
                CONSTRAINT fk_datafeed_src
                    FOREIGN KEY (datafeed_src_id)
                    REFERENCES datafeed_src (id)
                    ON DELETE SET NULL
                    ON UPDATE CASCADE,
                UNIQUE (security_id, datetime, datafeed_src_id)
            )
        '''
        self._db.execute(sql)



    def _create_schema_table_stock_adjustment(self):
        """
        Create the stock_adjustment table.

        Dependent on enums: None
        Dependent on tables: datafeed_src, security

        Subclass must define and execute SQL/etc.
        """
        sql = '''
            CREATE TABLE IF NOT EXISTS stock_adjustment (
                id integer NOT NULL GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                security_id integer NOT NULL,
                CONSTRAINT fk_security
                    FOREIGN KEY (security_id)
                    REFERENCES security (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                date date NOT NULL,
                factor double precision NOT NULL,
                dividend double precision,
                split_ratio double precision,
                datafeed_src_id integer NOT NULL,
                CONSTRAINT fk_datafeed_src
                    FOREIGN KEY (datafeed_src_id)
                    REFERENCES datafeed_src (id)
                    ON DELETE CASCADE
                    ON UPDATE CASCADE,
                UNIQUE (security_id, date, datafeed_src_id)
            )
        '''
        self._db.execute(sql)



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

        Raises:
          [Pass through expected]
        """
        _validate_cols(data.keys(), model_cls)
        val_vars = _prep_sanitized_vars('i', data)
        sql = f'''
            INSERT INTO {model_cls.get_table_name()}
            ({','.join(data.keys())})
            VALUES ({_build_var_list_str(val_vars.keys())})
        '''
        self._db.execute(sql, val_vars, **kwargs)



    def update(self, model_cls, data, where, **kwargs):
        """
        Update record(s) in the database.  The table is acquired from the model
        class.

        Subclass must define and execute SQL/etc.

        Args:
          model_cls (Class<Model<>>): The class itself of the model being
            updated.
          data ({str:str/int/bool/datetime/enum/etc}): The data to be updated,
            where the keys are the column names and the values are the
            python-type values to be used as the new values.
          where ({}/[]/() or None): The structured where clause.  See the
            Model.query_direct() docs for spec.  If None, will not filter.
          **kwargs ({}): Any additional paramaters that may be used by other
            methods: `Database.execute()`.  See those docstrings for more
            details.

        Raises:
          [Pass through expected]
        """
        _validate_cols(data.keys(), model_cls)
        val_vars = _prep_sanitized_vars('u', data)
        sql = f'''
            UPDATE {model_cls.get_table_name()}
            SET {_build_col_var_list_str(list(data), list(val_vars))}
        '''
        if where:
            where_clause, where_vars = _build_where(where, model_cls)
            sql += f' WHERE {where_clause}'
        else:
            where_vars = {}
        self._db.execute(sql, {**val_vars, **where_vars}, **kwargs)



    def delete(self, model_cls, where, really_delete_all=False, **kwargs):
        """
        Delete record(s) in the database.  The table is acquired from the model
        class.

        Subclass must define and execute SQL/etc.

        Args:
          model_cls (Class<Model<>>): The class itself of the model being
            deleted.
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

        Raises:
          [Pass through expected]
        """
        sql = f'DELETE FROM {model_cls.get_table_name()}'
        if where:
            where_clause, where_vars = _build_where(where, model_cls)
            sql += f' WHERE {where_clause}'
        elif really_delete_all:
            # Confirmed -- will allow deleting all by skipping where clause
            where_vars = {}
        else:
            err_msg = 'Invalid delete parameters: `where` empty, but did not' \
                    + ' set `really_delete_all` to confirm delete all.' \
                    + '  Likely intended to specify `where`?'
            logger.error(err_msg)
            raise ValueError(err_msg)
        self._db.execute(sql, where_vars, **kwargs)



    def query(self, model_cls, return_as, columns_to_return=None,
            where=None, limit=None, order=None, **kwargs):
        """
        Query/Select record(s) from the database.  The table is acquired from
        the model class.  This gives a few options as far as how the data can be
        returned.  Some of the typical query options are included, but some like
        the where and order clauses have a structured input that must be used.

        Subclass must define and execute SQL/etc.

        Args:
          model_cls (Class<Model<>>): The class itself of the model being
            queried.
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

        Raises:
          [Pass through expected]
        """
        if columns_to_return:
            _validate_cols(columns_to_return, model_cls)
            col_list_str = ','.join(columns_to_return)
        else:
            col_list_str = '*'

        sql = f'SELECT {col_list_str} FROM {model_cls.get_table_name()}'

        if where:
            where_clause, where_vars = _build_where(where, model_cls)
            sql += f' WHERE {where_clause}'
        else:
            where_vars = {}

        sql += ' ' + _build_and_validate_order(order, model_cls)
        sql += ' ' + _build_and_validate_limit(limit)

        # Must force cursor to stay open until results parsed
        cursor = self._db.execute(sql, where_vars,
                **{**kwargs, **{'close_cursor': False}})

        if model_meta.ReturnAs(return_as) is model_meta.ReturnAs.MODEL:
            results = self._convert_cursor_to_models(model_cls, cursor)
        elif model_meta.ReturnAs(return_as) is model_meta.ReturnAs.PANDAS:
            results = PostgresOrm._convert_cursor_to_pandas_dataframe(cursor)

        if 'close_cursor' not in kwargs or kwargs['close_cursor'] is True:
            cursor.close()

        return results



    def _convert_cursor_to_models(self, model_cls, cursor):
        """
        Converts the results in a cursor to a list of the specified Model.

        Args:
          model_cls (Class<Model<>>): The class itself of the models being
            created.
          cursor (cursor): The cursor from executing a query/select command,
            ready for results to be processed (i.e. NOT already iterated over).

        Returns:
          results ([model_cls]): A list of Models of the specific subclass of
            Model given by model_cls created from the cursor results.  An empty
            list if no results.
        """
        results = []
        cols = [d[0] for d in cursor.description]
        for row in cursor:
            results.append(model_cls(self, dict(zip(cols, row))))
        return results



    @staticmethod
    def _convert_cursor_to_pandas_dataframe(cursor):
        """
        Converts the results in a cursor to a pandas dataframe.

        Args:
          cursor (cursor): The cursor from executing a query/select command,
            ready for results to be processed (i.e. NOT already iterated over).

        Returns:
          (dataframe): The dataframe containing the data returned in the cursor.
        """
        return pd.DataFrame(cursor.fetchall(),
                columns=[d[0] for d in cursor.description])



def _validate_cols(cols, model_cls):
    """
    Validates the provided columns against those specified in the model.  Highly
    advised if the column names provided were potentially from an external user
    source instead of something hard-coded within the project to avoid SQL
    injection.

    Args:
      cols ([str]): The list of column names to check.
      model_cls (Class<Model<>>): The class itself of the model holding the
        valid column names.

    Raises:
      (NonexistentColumnError): Raised if any column provided does not exist in
        the official list of columns in the provided model.
    """
    # Check cols to avoid SQL injection in case `data` is from external
    valid_cols = model_cls.get_columns()
    if not set(cols).issubset(valid_cols):
        err_msg = f'Invalid column(s) for {model_cls.__name__}:'
        err_msg += f' `{"`, `".join(set(cols) - set(valid_cols))}`'
        logger.error(err_msg)
        raise orm_meta.NonexistentColumnError(err_msg)



def _prep_sanitized_vars(prefix, data):
    """
    Prepares parameterized variables for SQL statements for sanitized entry.

    Args:
      prefix (str): The prefix to give the variable placeholder names.  The
        format is <prefix>val<count>.  This can be an empty string, but must be
        unique within a given SQL statement (e.g. in an update statement, since
        there are values for updating as well as possible values in the where
        clause, calling this for each of those portions should use a different
        prefix to give it a different namespace and avoid dict collisions).
      data ({str:str/int/bool/datetime/enum/etc}): The data to be prepared,
            where the keys are the column names and the values are the
            python-type values to be used as the variable values.

    Returns:
      val_vars ({str:str/int/bool/datetime/enum/etc}): The mapping of variable
        names to be used in the SQL statement to their corresponding values.
        These variable names in the key portion of this dict are intended to be
        used in the `%(<>)s` format in the SQL statement.  These are in the same
        order as the column names -- Python 3.7+ REQUIRED.
    """
    val_vars = {}
    for col in data:
        val_vars[f'{prefix}val{len(val_vars)}'] = data[col]
    return val_vars



def _build_var_list_str(var_names):
    """
    Builds the string that contains the list of variables in the parameterized
    variable format for SQL statements.

    Args:
      var_names ([str]): The list of var names, likely the keys in the dict
        returned by `_prep_sanitized_vars()`.

    Returns:
      (str): The single string that contains the list of all variable names
        provided in comma-separated format, but as parameterized inputs (i.e.
        `%(<>)s` format).  An empty string if no var names.
    """
    return ', '.join([f'%({v})s' for v in var_names])



def _build_col_var_list_str(col_names, var_names):
    """
    Builds the string that contains the list of column to parameterized variable
    assignments for SQL statements.

    Args:
      col_names ([str]): The list of column names.  Order and length MUST match
        that of `var_names`!
      var_names ([str]): The list of var names, likely the keys in the dict
        returned by `_prep_sanitized_vars()`.  Order and length MUST match that
        of `col_names`!

    Returns:
      (str): The single string that contains the list of all <col> = <var>`
        items in comma-separated format, where the vars are parameterized inputs
        (i.e. `%(<>)s`).  An emptry string if no col/var names
    """
    assert len(col_names) == len(var_names), 'Col and vars must be same length!'
    return ', '.join([f'{col_names[i]} = %({var_names[i]})s'
            for i in range(len(col_names))])



def _build_where(where, model_cls=None):
    """
    Builds the full where clause from the structured where format.  See
    `Model.query_direct()` for details of the format.

    Args:
      where ({}/[]/() or None): The structured where clause.  See the
        Model.query_direct() docs for spec.  If None, will not filter.
      model_cls (Class<Model<>> or None): The class itself of the model holding
        the valid column names.  Can be None if skipping that check for
        increased performance, but this is ONLY recommended if the source of the
        column names in the structured `where` parameter is internally
        controlled and was not subject to external user input to avoid SQL
        injection attacks.

    Returns:
      clause (str): The single string clause containing logic statements to use
        as the where clause, including parameterized inputs for variables (i.e.
        `%(<>)s` format).  This does NOT include the `WHERE` part of the string.
        An empty string if nothing specified for `where`.
      vals ({str:str/int/bool/datetime/enum/etc}): The mapping of variable names
        as they will be used within parameterized format (i.e. `%(<>)s` format)
        in the returned `clause`.  All variable names (i.e. the keys) follow the
        naming convention `wval{count}` to avoid collisions with variables
        derived separately for values in an update clause, for example.  An
        empty dict if nothing specified for `where`.
    """
    vals = {}
    if not where:
        clause = ''
    elif len(where) == 1:
        logic_combo, conds = next(iter(where.items()))
        clause = _build_conditional_combo(logic_combo, conds, vals, model_cls)
    else:
        clause = _build_conditional_single(where, vals, model_cls)
    return clause, vals



def _build_conditional_combo(logic_combo, conds, vals, model_cls=None):
    """
    Builds the combinational conditional portion of a where clause, calling
    itself again recursively as needed.

    Args:
      logic_combo (LogicCombo): The specified way to logically combine all
        immediate/shallow elements of the conditions in `conds`.
      conds ([{}/[]/()]): The list of conditions, where each condition can be a
        single condition spec or can be another combinational spec.  See the
        Model.query_direct() docs for spec.
      vals ({str:str/int/bool/datetime/enum/etc}): The mapping of variable names
        as they will be used within parameterized format (i.e. `%(<>)s` format)
        in the returned `clause`.  This is expected to contain all variables
        already built into the where clause currently being processed and will
        be modified by single conditional specs when they specify variables.
      model_cls (Class<Model<>> or None): The class itself of the model holding
        the valid column names.  Can be None if skipping that check for
        increased performance, but this is ONLY recommended if the source of the
        column names in the structured `where` parameter is internally
        controlled and was not subject to external user input to avoid SQL
        injection attacks.

    Returns:
      (str): The portion of the clause that combines all provided conditionals
        by the specified logic combinational element, wrapped in parentheses for
        safe continued combination.  Note that the `vals` provided will be
        modified by adding any new variables included in this portion of the
        clause.

    Raises:
      (ValueError): Raised if the `logic_combo` provided is not a valid
        LogicCombo option for this Orm.
    """
    cond_strs = []
    for cond in conds:
        if len(cond) == 1:
            sub_logic_combo, sub_conds = next(iter(cond.items()))
            cond_strs.append(_build_conditional_combo(sub_logic_combo,
                    sub_conds, vals, model_cls))
        else:
            cond_strs.append(_build_conditional_single(cond, vals, model_cls))

    if logic_combo is model_meta.LogicCombo.AND:
        logic_combo_str = ' AND '
    elif logic_combo is model_meta.LogicCombo.OR:
        logic_combo_str = ' OR '
    else:
        err_msg = f'Invalid or Unsupported Logic Combo: {logic_combo}'
        logger.error(err_msg)
        raise ValueError(err_msg)

    return '(' + logic_combo_str.join(cond_strs) + ')'



def _build_conditional_single(cond, vals, model_cls=None):
    """
    Builds the single conditional portion of a where clause.

    Args:
      cond (()/[]): The tuple/list containing the elements for a single
        conditional statement.  See Model.query_direct() docs for full details
        on the format.
      vals ({str:str/int/bool/datetime/enum/etc}): The mapping of variable names
        as they will be used within parameterized format (i.e. `%(<>)s` format)
        in the returned `clause`.  This is expected to contain all variables
        already built into the where clause currently being processed and will
        be modified here if a value/variable is part of the conditional.
      model_cls (Class<Model<>> or None): The class itself of the model holding
        the valid column names.  Can be None if skipping that check for
        increased performance, but this is ONLY recommended if the source of the
        column names in the structured `where` parameter is internally
        controlled and was not subject to external user input to avoid SQL
        injection attacks.

    Returns:
      (str): The portion of the clause that represents this single conditional.
        Any variables will be in parameterized format (i.e. `%(<>)s` format).
        Note that the `vals` provided will be modified by adding any new
        variables included in this portion of the clause.

    Raises:
      (NonexistentColumnError): Raised if the column provided in the `cond` does
        not exist in the official list of columns in the provided model (only
        possible if model_cls provided as non-None).
      (ValueError): Raised if the LogicOp provided as part of the `cond` is not
        a valid LogicOp option for this Orm.
    """
    if model_cls is not None:
        _validate_cols([cond[0]], model_cls)

    if cond[1] is model_meta.LogicOp.NOT_NULL:
        return f'{cond[0]} NOT NULL'

    # The rest below have a value, so all would use same key
    val_key = f'wval{str(len(vals))}'

    if cond[1] is model_meta.LogicOp.EQ \
            or cond[1] is model_meta.LogicOp.EQUAL \
            or cond[1] is model_meta.LogicOp.EQUALS:
        vals[val_key] = cond[2]
        return f'{cond[0]} = %({val_key})s'

    if cond[1] is model_meta.LogicOp.LT \
            or cond[1] is model_meta.LogicOp.LESS_THAN:
        vals[val_key] = cond[2]
        return f'{cond[0]} < %({val_key})s'

    if cond[1] is model_meta.LogicOp.LTE \
            or cond[1] is model_meta.LogicOp.LESS_THAN_OR_EQUAL:
        vals[val_key] = cond[2]
        return f'{cond[0]} <= %({val_key})s'

    if cond[1] is model_meta.LogicOp.GT \
            or cond[1] is model_meta.LogicOp.GREATER_THAN:
        vals[val_key] = cond[2]
        return f'{cond[0]} > %({val_key})s'

    if cond[1] is model_meta.LogicOp.GTE \
            or cond[1] is model_meta.LogicOp.GREATER_THAN_OR_EQUAL:
        vals[val_key] = cond[2]
        return f'{cond[0]} >= %({val_key})s'

    err_msg = f'Invalid or Unsupported Logic Op: {cond[1]}'
    logger.error(err_msg)
    raise ValueError(err_msg)



def _build_and_validate_order(order, model_cls=None):
    """
    Builds the full order clause from the structured order format, validating as
    it goes.  See `Model.query_direct()` for details of the format.

    Args:
      order ([()]): The structured order clause.  See the Model.query_direct()
        docs for spec.
      model_cls (Class<Model<>> or None): The class itself of the model holding
        the valid column names.  Can be None if skipping that check for
        increased performance, but this is ONLY recommended if the source of the
        column names in the structured `where` parameter is internally
        controlled and was not subject to external user input to avoid SQL
        injection attacks.

    Returns:
      (str): The single string clause containing the the statements to use as
        the ORDER BY clause.  This DOES include the `ORDER BY` part of the
        string.  An empty string if nothing specified for `where`.

    Raises:
      (NonexistentColumnError): Raised if any column provided in the `order`
        does not exist in the official list of columns in the provided model
        (only possible if model_cls provided as non-None).
      (ValueError): Raised if the SortOrder provided as part of the `order` is
        not a valid SortOrder option for this Orm.
    """
    if not order:
        return ''

    order_strs = []

    try:
        for col, odir in order:
            if model_cls is not None:
                _validate_cols([col], model_cls)

            if odir is model_meta.SortOrder.ASC:
                order_strs.append(f'{col} ASC')
            elif odir is model_meta.SortOrder.DESC:
                order_strs.append(f'{col} DESC')
            else:
                err_msg = f'Invalid or Unsupported Sort Order: {odir}'
                logger.error(err_msg)
                raise ValueError(err_msg)

    except ValueError as ex:
        err_msg = f'Failed to parse sort order: {ex}'
        logger.error(err_msg)
        raise ValueError(err_msg) from ex

    return f'ORDER BY {", ".join(order_strs)}'



def _build_and_validate_limit(limit):
    """
    Builds the full limit clause from the limit number format, validating as it
    goes.

    Args:
      limit (int): The maximum number of records to return.

    Returns:
      (str): The single string clause containing the the statements to use as
        the LIMIT clause.  This DOES include the `LIMIT` part of the string.  An
        empty string if nothing specified for `where`.

    Raises:
      (ValueError): Raised if the limit provided is not an integer.
    """
    if limit is None:
        return ''

    try:
        limit_num = int(limit)
        return f'LIMIT {limit_num}'

    except ValueError as ex:
        err_msg = f'Failed to parse limit, likely not a number: {ex}'
        logger.error(err_msg)
        raise ValueError(err_msg) from ex
