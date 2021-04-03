#!/usr/bin/env python3
"""
Tests the grand_trade_auto.web.backend.main functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  client (TestClient): The test client to use from fastapi to mock a client in
    tests.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from fastapi.testclient import TestClient

from grand_trade_auto.web.backend import main



client = TestClient(main.app)



def test_get_root():
    """
    Tests `get_root()`.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert response.json() == {'msg': 'Root page'}
