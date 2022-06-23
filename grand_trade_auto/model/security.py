#!/usr/bin/env python3
"""
The Security data model.  Largely just defines the table and columns.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.model import model_meta



class Security(model_meta.Model):
    """
    The Security data model for the database.

    Class Attributes:
      exchange_id (int): [Column var] The foreign key for the exchange on which
        this security is traded (and on which its ticker symbol is valid).
      ticker (str): [Column var] The ticker symbol on which this trades, such
        as "AAPL" for "Apple".
      market (Enum(Market)): [Column var] The type of market that this trades in
        (e.g. stock, crypto, futures, etc.).
      name (str): [Column var] The name of the security.  Mostly the company
        name, but may include information such as preferred stock, etc.
      company_id (int): [Column var] The company to which this security belongs.
        Multiple securities may belong to a single company in the event of
        different types of shares (preferred vs non-voting, etc.).
      currency (Enum(Currency)): [Column var] The currency in which this
        security trades.  All prices are in this currency!
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
    _table_name = 'security'

    _columns = (
        'id',
        'exchange_id',
        'ticker',
        'market',
        'name',
        'company_id',
        'currency',
        # 'listing_date',
        # 'delisting_date',
        # TODO: Add date retired/removed or whatever (need start too?) (terms are listing/delisting)
        'datafeed_src_id',
    )

    _read_only_columns = (
        'id',
    )

    # Column Attributes -- MUST match _columns!
    # id defined in super
    exchange_id = None
    ticker = None
    market = None
    name = None
    company_id = None
    currency = None
    datafeed_src_id = None
    # End of Column Attributes
