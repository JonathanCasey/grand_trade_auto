#!/usr/bin/env python3
"""
Tests the grand_trade_auto.apic.apics functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
#pylint: disable=protected-access  # Allow for purpose of testing those elements

import pytest

from grand_trade_auto.apic import apics



def test_load_and_set_main_apic_from_config():
    """
    Tests that the `load_and_set_main_apic_from_config()` method.
    """
    with pytest.raises(AssertionError):
        apics.load_and_set_main_apic_from_config('invalid-env')
    assert apics._APIC is None

    apics.load_and_set_main_apic_from_config('test', 'alpaca')
    assert apics._APIC is not None
    assert apics._APIC._rest_api is not None

    with pytest.raises(AssertionError):
        apics.load_and_set_main_apic_from_config('test')
    assert apics._APIC is not None



def test_get_apic_from_config():
    """
    Tests that the `_get_apic_from_config()` method.
    """
    assert apics._get_apic_from_config('invalid-env') is None
    assert apics._get_apic_from_config('test', 'invalid-type') is None
    assert apics._get_apic_from_config('test') is not None
    assert apics._get_apic_from_config('test', 'alpaca') is not None
