#!/usr/bin/env python3
"""
Tests the grand_trade_auto.general.dirs functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.general import utils



def test_bypass_for_test(monkeypatch):
    """
    Tests `bypass_name_main_for_test()`.
    """
    assert not utils.bypass_for_test(test_bypass_for_test,
            1)

    def allow_test_bypass_for_test(mod_or_meth_ref, sub_id):
        """
        Will allow a specific case to pass in order to test bypass.

        Args: Same as utils.bypass_for_test().
        """
        if mod_or_meth_ref == test_bypass_for_test \
                and sub_id == 2:   # pylint: disable=comparison-with-callable
            return True
        return False

    original_bypass_for_test = utils.bypass_for_test
    monkeypatch.setattr(utils, 'bypass_for_test', allow_test_bypass_for_test)
    assert not utils.bypass_for_test(test_bypass_for_test, 1)
    assert utils.bypass_for_test(test_bypass_for_test, 2)

    monkeypatch.setattr(utils, 'bypass_for_test', original_bypass_for_test)
    assert not utils.bypass_for_test(test_bypass_for_test, 2)
