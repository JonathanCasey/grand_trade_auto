#!/usr/bin/env python3
"""Tests the grand_trade_auto.general.dirs functionality.

Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import os.path

from grand_trade_auto.general import dirs



def test_get_root_path():
    """Tests that the `get_root_path()` method will return the correct result
    by verifying the same result via this alternate traversal path.
    """
    general_unit_test_dir = os.path.dirname(os.path.realpath(__file__))
    unit_test_dir = os.path.dirname(general_unit_test_dir)
    test_dir = os.path.dirname(unit_test_dir)
    root_repo_dir = os.path.dirname(test_dir)
    assert root_repo_dir == dirs.get_root_path()
