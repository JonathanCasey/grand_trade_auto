#!/usr/bin/env python3
"""
The Datafeed Source data model.  Largely just defines the table and columns.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.model import model_meta



class DatafeedSrc(model_meta.Model):
    """
    The Datafeed Source data model for the database.

    Class Attributes:
      config_parser (str): [Column var] The config parser representation for
        this datafeed's configuration at time data was saved.
      is_init_complete (bool): [Column var] True if initialization complete;
        False/None if not complete or not even started.
      progress_marker (str): [Column var] Marks the progress on executing an
        ongoing datafeed import action.  Format TBD.

      [inherited from Model]:
        _table_name (str or None): The name of the table in the database.
          Subclasses should override and then never change...
        _columns ([str] or None): The list of column names in the table.  These
          should each have a class attribute with a matching name for ease of
          access.  Subclasses should override this with the name of columns and
          then never change...
        id (int or None): [Column var] The value of the id column in the table for
          this record.  All tables MUST have an id field, at least until some
          TSDB shows up.  As a class attribute, this is intended to hold some
          default value.  It will be superseded its corresponding instance
          variable upon being written to.  This is the practice for all
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
    _table_name = 'datafeed_src'

    _columns = (
        'id',
        'config_parser',
        'is_init_complete',
        'progress_marker',
    )

    # Column Attributes -- MUST match _columns!
    # id defined in super
    config_parser = None
    is_init_complete = None
    progress_marker = None
    # End of Column Attributes
