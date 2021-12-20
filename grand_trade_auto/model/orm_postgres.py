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
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from grand_trade_auto.model import model_meta
from grand_trade_auto.model import orm_meta



logger = logging.getLogger(__name__)



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
        sql = '''CREATE TABLE datafeed_src (
            id serial PRIMARY KEY,
            config_parser text NOT NULL,
            is_init_complete boolean,
            progress_marker text,
            UNIQUE (config_parser)
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
        """
        _validate_cols(model_cls, data.keys())
        val_vars = _prep_sanitized_vars('i', data)
        sql = f'''INSERT INTO {model_cls.get_table_name()}
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
          model_cls (Class<Model<>>): The class itself of the model being added.
          data ({str:str/int/bool/datetime/enum/etc}): The data to be updated,
            where the keys are the column names and the values are the
            python-type values to be used as the new values.
          where ({}/[]/() or None): The structured where clause.  See the
            Model.query_direct() docs for spec.  If None, will not filter.
        """
        _validate_cols(model_cls, data.keys())
        val_vars = _prep_sanitized_vars('u', data)
        sql = f'''UPDATE {model_cls.get_table_name()}
            SET {_build_col_var_list_str(data.keys(), val_vars.keys())}
            VALUES ({_build_var_list_str(val_vars.keys())})
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



def _validate_cols(model_cls, cols):
    """
    """
    # Check cols to avoid SQL injection in case `data` is from external
    valid_cols = model_cls.get_columns()
    if not set(cols).issubset(valid_cols):
        err_msg = f'Invalid columns for {model_cls.__name__}: '
        err_msg += f' `{["`, `".join(set(cols) - set(valid_cols))]}`'
        logger.error(err_msg)
        raise orm_meta.NonexistentColumnError(err_msg)



def _prep_sanitized_vars(prefix, data):
    """
    """
    val_vars = {}
    for col in data:
        val_vars[f'{prefix}val{len(val_vars)}'] = data[col]
    return val_vars



def _build_var_list_str(var_names):
    """
    """
    return ', '.join([f'%({v})s' for v in var_names])



def _build_col_var_list_str(col_names, var_names):
    """
    """
    assert len(col_names) == len(var_names), 'Col and vars must be same length!'
    return ', '.join([f'{col_names[i]} = %({var_names[i]})s'
            for i in range(len(col_names))])



def _build_where(where, model_cls=None):
    """
    """
    vals = {}
    if len(where) == 1:
        logic_combo, conds = next(iter(where.items()))
        clause = _build_conditional_combo(logic_combo, conds, vals, model_cls)
    else:
        clause = _build_conditional_single(where, vals, model_cls)
    return clause, vals



def _build_conditional_combo(logic_combo, conds, vals, model_cls=None):
    """
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

    return '(' + logic_combo_str.join(cond_strs) + ')'



def _build_conditional_single(cond, vals, model_cls=None):
    """
    """
    if model_cls is not None and not _validate_cols(model_cls, [cond[0]]):
        err_msg = f'Invalid column for {model_cls.__name__}: `{cond[0]}`'
        logger.error(err_msg)
        raise orm_meta.NonexistentColumnError(err_msg)

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
