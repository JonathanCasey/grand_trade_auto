#!/usr/bin/env python3
"""
Tests the grand_trade_auto.web.frontend.templates.root_index.jinja2
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
import markupsafe
import pytest

from . import standard as templates_std
from . import utils as templates_utils



def test_html_head():
    """
    Tests the contents of the head tag in the HTML is as expected.
    """
    context = {
        'data': {},
    }
    html = templates_utils.render_sanitized_from_file('root_index.jinja2',
            context)
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.head.title.contents[0] == 'Root Index Page'
    templates_std.are_style_sheets_scripts_present(html)



def test_template_fields():
    """
    Tests the jinja2 template fields in 'root_index.jinja2'.
    """
    context = {
        'data': {
            'test_msg': 'Jinja2 test',
        },
    }
    html = templates_utils.render_sanitized_from_file('root_index.jinja2',
            context)
    assert 'Jinja2 test' in html

    context = {
        'data': {},
    }
    html = templates_utils.render_sanitized_from_file('root_index.jinja2',
            context)
    assert 'Jinja2 test' not in html
    # Also tests that it renders at all

    context = {
        'data': {
            'test_msg': '<p>Jinja2 test</p>',
        },
    }
    html = templates_utils.render_sanitized_from_file('root_index.jinja2',
            context)
    assert '&lt;p&gt;Jinja2 test&lt;/p&gt;' in html

    context = {
        'data': {
            'test_msg': markupsafe.Markup('<p>Jinja2 test</p>'),
        },
    }
    html = templates_utils.render_sanitized_from_file('root_index.jinja2',
            context)
    assert '<p>Jinja2 test</p>' in html

    context = {}
    with pytest.raises(jinja2.exceptions.UndefinedError) as ex:
        html = templates_utils.render_sanitized_from_file('root_index.jinja2',
                context)
    assert "'data' is undefined" in str(ex.value)
