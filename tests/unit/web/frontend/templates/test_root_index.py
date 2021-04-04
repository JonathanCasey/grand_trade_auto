#!/usr/bin/env python3
"""
Tests the grand_trade_auto.web.frontend.templates.root_index.html jinja2
rendering / functionality.

Per [pytest](https://docs.pytest.org/en/reorganize-docs/new-docs/user/naming_conventions.html),
all tiles, classes, and methods will be prefaced with `test_/Test` to comply
with auto-discovery (others may exist, but will not be part of test suite
directly).

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from bs4 import BeautifulSoup
import jinja2
import pytest

from . import standard as tt_std
from . import utils as tt_utils



def test_html_head():
    """
    Tests the contents of the head tag in the HTML is as expected.
    """
    context = {
        'data': {},
    }
    html = tt_utils.render_sanitized('root_index.html', context)
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.head.title.contents[0] == 'Root Index Page'
    tt_std.are_style_sheets_scripts_present(html)



def test_template_fields():
    """
    Tests the jinja2 template fields in 'root_index.html'.
    """
    context = {
        'data': {
            'test_msg': 'Jinja2 test',
        },
    }
    html = tt_utils.render_sanitized('root_index.html', context)
    assert 'Jinja2 test' in html

    context = {
        'data': {},
    }
    html = tt_utils.render_sanitized('root_index.html', context)
    assert 'Jinja2 test' not in html
    # Also tests that it renders at all

    context = {}
    with pytest.raises(jinja2.exceptions.UndefinedError) as ex:
        html = tt_utils.render_sanitized('root_index.html', context)
    assert "'data' is undefined" in str(ex.value)
