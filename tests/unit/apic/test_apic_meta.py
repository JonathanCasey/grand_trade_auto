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
import logging

from grand_trade_auto.apic import alpaca
from grand_trade_auto.apic import apic_meta



def test_apic_init(caplog):
    """
    Tests the `__init__()` method of `Apic`, at least for its unique
    functionality that is not expected to be tested anywhere else.
    """

    class MockApicChild(apic_meta.Apic):
        """"
        Simple mock object to subclass Apic.
        """

        @classmethod
        def load_from_config(cls, apic_cp, apic_id, secrets_id):
            """
            Not needed / will not be used.
            """
            return

        @classmethod
        def get_provider_names(cls):
            """
            Not needed / will not be used.
            """
            return

        def connect(self):
            """
            Not needed / will not be used.
            """
            return

    caplog.set_level(logging.WARNING)
    caplog.clear()
    MockApicChild('mock_env', 'mock_cp_apic_id', 'mock_cp_secrets_id')
    assert caplog.record_tuples == []

    extra_kwargs = {
            'key1': 'val1',
            'key2': 'val2',
    }
    caplog.clear()
    MockApicChild('mock_env', 'mock_cp_apic_id', 'mock_cp_secrets_id',
            **extra_kwargs)
    assert caplog.record_tuples == [
            ('grand_trade_auto.apic.apic_meta', logging.WARNING,
                'Discarded excess kwargs provided to MockApicChild: key1, key2')
    ]

    # Using Alpaca to test grandchild with multiple/diamond inheritance pattern
    kwargs = {
        'env': 'mock_env',
        'cp_apic_id': 'mock_cp_apic_id',
        'cp_secrets_id': 'mock_cp_secrets_id',
        **extra_kwargs,
    }
    caplog.clear()
    alpaca.Alpaca('paper', **kwargs)
    assert caplog.record_tuples == [
            ('grand_trade_auto.apic.apic_meta', logging.WARNING,
                'Discarded excess kwargs provided to Alpaca: key1, key2')
    ]
