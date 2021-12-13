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
#pylint: disable=use-implicit-booleaness-not-comparison
#   +-> want to specifically check type in most tests -- `None` is a fail

from grand_trade_auto.apic import alpaca
from grand_trade_auto.apic import apics



def test_get_apic(monkeypatch):
    """
    Tests that the `get_apic()` method.
    """
    assert apics.get_apic('invalid-apic-id') is None
    assert apics._apics_loaded == {}

    assert apics.get_apic('alpaca-test', 'invalid-env') is None
    assert apics._apics_loaded == {}

    assert apics.get_apic('alpaca-test') is not None
    assert apics._apics_loaded != {}

    apics._apics_loaded.pop('alpaca-test')
    assert apics._apics_loaded == {}

    assert apics.get_apic('alpaca-test', 'test') is not None
    assert apics._apics_loaded != {}

    def mock_get_apic_from_config(
            apic_id, env=None):                # pylint: disable=unused-argument
        """
        Replaces the `_get_apic_from_config()` so it will find no match.
        """
        return None

    monkeypatch.setattr(apics, '_get_apic_from_config',
            mock_get_apic_from_config)

    assert apics.get_apic('alpaca-test') is not None

    assert apics.get_apic('alpaca-test', 'test') is not None



def test_get_apic_from_config(monkeypatch):
    """
    Tests that the `_get_apic_from_config()` method.
    """
    assert apics._get_apic_from_config('invalid-apic-id') is None
    assert apics._get_apic_from_config('alpaca-test', 'invalid-env') is None
    assert apics._get_apic_from_config('alpaca-test') is not None
    assert apics._get_apic_from_config('alpaca-test', 'test') is not None

    def mock_get_provider_names():
        """
        Replaces the `get_provider_names()` in an API Client so it will find no
        match.
        """
        return []

    monkeypatch.setattr(alpaca.Alpaca, 'get_provider_names',
            mock_get_provider_names)

    assert apics._get_apic_from_config('alpaca-test') is None
