#!/usr/bin/env python3
"""
The StockAdjustment data model.  Largely just defines the table and columns.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.model import model_meta



class StockAdjustment(model_meta.Model):
    """
    The StockAdjustment data model for the database.

    Class Attributes:
      security_id (int): [Column var] The foreign key for the security for which
        this adjustment applies.
      date (Date): [Column var] The data of the adjustment.  Applies at the
        close of that business/trading day.
      factor (float): The net factor to apply to historical prices based on this
        adjustment, regardless of whether it is a dividend or split or rights
        offer.  For example, a 4-for-1 split will x4 the number of shares, so it
        will cut all prices to 1/4; therefore, this would store 0.25 to be
        multiplied by those earlier prices to calculate the equivalent price per
        share as it would exist today.  For splits, the volume is divided by
        this value to find the adjusted volume.
      dividend (float): [Column var] The amount per share for a dividend, if
        any.
      split_ratio (float): [Column var] The split ratio of new shares to old
        shares.  For example, a 4-for-1 split will give each share holder 4
        shares for every 1 share; therefore, a 4 would be stored here to signify
        an increase in the number of shares by that factor.
      datafeed_src_id (int): [Column var] The foreign key for the datafeed
        source that last set this data.

      [inherited from Model]:
        _table_name (str or None): The name of the table in the database.
          Subclasses should override and then never change...
        _columns ((str) or None): The tuple of column names in the table.  These
          should each have a class attribute with a matching name for ease of
          access.  Subclasses should override this with the name of columns and
          then never change...
        _read_only_columns ((str)): The tuple of column names in the table that
          are read only.  These may be, for example, the `id` column that is
          auto-incremented and cannot be written to by a user.  These should be
          a subset of the `_columns`.  Subclasses should override this with the
          name of columns (or an empty list) and then never change...
        id (int or None): [RO Column var] The value of the id column in the
          table for this record.  All tables MUST have an id field, at least
          until some TSDB shows up.  As a class attribute, this is intended to
          hold some default value.  It will be superseded its corresponding
          instance variable upon being written to.  This is the practice for all
          column-related attributes.

    Instance Attributes:
      [All Class Attributes named in _columns are instance attributes when used]

      [inherited from Model]:
        _orm (Orm): The ORM that is being used to interact with the
          database for this model.
        _active_cols (set(str)): The columns that are "active" in this record.
          This will essentially exclude any columns that were not pulled from
          the database nor were written to here so that, in the event of an
          update, only the columns populated here will be updated.  Subclasses
          should not need to touch this.
    """
    _table_name = 'stock_adjustment'

    _columns = (
        'id',
        'security_id',
        'date',
        'factor',
        'dividend',
        'split_ratio',
        'datafeed_src_id',
    )

    _read_only_columns = (
        'id',
    )

    # Column Attributes -- MUST match _columns!
    # id defined in super
    security_id = None
    date = None
    factor = None
    dividend = None
    split_ratio = None
    datafeed_src_id = None
    # End of Column Attributes
