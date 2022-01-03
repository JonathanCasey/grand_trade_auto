#!/usr/bin/env python3
"""
The SecurityPrice data model.  Largely just defines the table and columns.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.model import model_meta



class SecurityPrice(model_meta.Model):
    """
    The SecurityPrice data model for the database.

    Class Attributes:
      security_id (long int): [Column var] The foreign key for the security for which
        this price applies.
      datetime (Datetime): [Column var] The datatime of the price.  For daily
        or longer price frequencies, only the date portion should be used -- the
        time portion is not guaranteed to be any specific value.  This IS a
        timezone-aware datetime.
      raw_open (float): [Column var] The opening price as reported at the time of
        occurrence (i.e. without any historical adjustments applied).
      raw_close (float): [Column var] The closing price as reported at the time
        of occurrence (i.e. without any historical adjustments applied).
      raw_high (float): [Column var] The high price as reported at the time of
        occurrence (i.e. without any historical adjustments applied).
      raw_low (float): [Column var] The low price as reported at the time of
        occurrence (i.e. without any historical adjustments applied).
      raw_volume (long int): [Column var] The volume as reported at the time of
        occurrence (i.e. without any historical adjustments applied).
      adj_open (float): [Column var] The opening price as it would exist today
        after accounting for historical adjustments such as splits, dividends.
      adj_close (float): [Column var] The closing price as it would exist today
        after accounting for historical adjustments such as splits, dividends.
      adj_high (float): [Column var] The high price as it would exist today
        after accounting for historical adjustments such as splits, dividends.
      adj_low (float): [Column var] The low price as it would exist today after
        accounting for historical adjustments such as splits, dividends.
      adj_volume (long int): [Column var] The volume as it would exist today
        after accounting for historical adjustments such as splits, dividends.
      is_intraperiod (bool): [Column var] True if this is an unfinished period
        and therefore the data may be incomplete (e.g. close may be at time of
        storage rather than the true "final" close when the period finishes).
        False if data for the period is fully available.
      frequency (Enum(PriceFrequency)): [Column var] The frequency/period that
        this data represents (e.g. 5 min bars, daily, etc.).
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
    _table_name = 'security_price'

    _columns = (
        'id',
        'security_id',
        'datetime',
        'raw_open',
        'raw_close',
        'raw_high',
        'raw_low',
        'raw_volume',
        'adj_open',
        'adj_close',
        'adj_high',
        'adj_low',
        'adj_volume',
        'is_intraperiod',
        'frequency',
        'datafeed_src_id',
    )

    _read_only_columns = (
        'id',
    )

    # Column Attributes -- MUST match _columns!
    # id defined in super
    security_id = None
    datetime = None
    raw_open = None
    raw_close = None
    raw_high = None
    raw_low = None
    raw_volume = None
    adj_open = None
    adj_close = None
    adj_high = None
    adj_low = None
    adj_volume = None
    is_intraperiod = None
    frequency = None
    datafeed_src_id = None
    # End of Column Attributes
