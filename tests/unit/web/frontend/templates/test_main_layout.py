#!/usr/bin/env python3
"""
Tests the grand_trade_auto.web.frontend.templates.main_layout.jinja2
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

from . import standard as templates_std
from . import utils as templates_utils



def test_html_head():
    """
    Tests the contents of the head tag in the HTML is as expected.
    """
    html = templates_utils.render_sanitized_from_file('main_layout.jinja2')
    templates_std.are_style_sheets_scripts_present(html)

    # Title tag tested as part of `test_template_fields()``



def test_template_fields():
    """
    Tests the jinja2 template fields in 'main_layout.jinja2'.
    """
    html = templates_utils.render_sanitized_from_file('main_layout.jinja2')
    assert '<html>' in html     # Just want to confirm any successful render

    template_str  = '{% extends "main_layout.jinja2" %}'
    template_str += '{% block title %}Test Title{% endblock %}'
    html = templates_utils.render_sanitized_from_str(template_str)
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.head.title.contents[0] == 'Test Title'

    template_str  = '{% extends "main_layout.jinja2" %}'
    template_str += '{% block body_content %}Test Body Content{% endblock %}'
    html = templates_utils.render_sanitized_from_str(template_str)
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.body.contents[0].strip() == 'Test Body Content'
