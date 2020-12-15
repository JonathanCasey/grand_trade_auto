#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.dirs functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Attributes:
  APP_NAME (str): The name of the app as it appears in its folder name in the
    repo root.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import os.path

from grand_trade_auto.general import dirs



APP_NAME = 'grand_trade_auto'



def get_root_path():
    """
    Gets the root path of this repo (in an alternate path/method than would
    be done in grand_trade_auto.general.dirs) for use in tests.

    Returns:
      root_repo_dir (os.path): The absolute path to the repo root dir.
    """
    general_unit_test_dir = os.path.dirname(os.path.realpath(__file__))
    unit_test_dir = os.path.dirname(general_unit_test_dir)
    test_dir = os.path.dirname(unit_test_dir)
    root_repo_dir = os.path.dirname(test_dir)
    return root_repo_dir



def test_get_root_path():
    """
    Tests that the `get_root_path()` method will return the correct result
    by verifying the same result via this alternate traversal path.
    """
    assert get_root_path() == dirs.get_root_path()



def test_get_src_app_root_path():
    """
    Tests that the `get_src_app_root_path()` method will return the correct
    result by verifying the same result via this alternate traversal path.
    """
    src_app_root_dir = os.path.join(get_root_path(), APP_NAME)
    assert src_app_root_dir == dirs.get_src_app_root_path()



def test_get_conf_path():
    """
    Tests that the `get_conf_path()` method will return the correct result by
    verifying the same result via this alternate traversal path.
    """
    conf_dir = os.path.join(get_root_path(), 'config')
    assert conf_dir == dirs.get_conf_path()
