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
import jinja2

from . import standard as tt_std    # TODO: Better name
from . import utils as tt_utils     # TODO: Better name



def test_html_head():
    """
    Tests the contents of the head tag in the HTML is as expected.
    """
    html = tt_utils.render_sanitized('main_layout.jinja2')
    tt_std.are_style_sheets_scripts_present(html)

    # Title tag tested as part of `test_template_fields()``



def test_template_fields():
    """
    Tests the jinja2 template fields in 'main_layout.jinja2'.
    """
    html = tt_utils.render_sanitized('main_layout.jinja2')
    assert '<html>' in html     # Just want to confirm any successful render

    main_layout_sanitized_filename = \
            tt_utils.SANITIZED_FILENAME_TEMAPLTE.substitute(
                filename='main_layout.jinja2')
    template_str  = '{% extends "' + main_layout_sanitized_filename + '" %}'
    template_str += '{% block title %}Test Title{% endblock %}'
    template = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                tt_utils.get_sanitized_jinja2_templates_test_path()
            )).from_string(template_str)
    html = template.render()
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.head.title.contents[0] == 'Test Title'


    main_layout_sanitized_filename = \
            tt_utils.SANITIZED_FILENAME_TEMAPLTE.substitute(
                filename='main_layout.jinja2')
    template_str  = '{% extends "' + main_layout_sanitized_filename + '" %}'
    template_str += '{% block body_content %}Test Body Content{% endblock %}'
    template = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                tt_utils.get_sanitized_jinja2_templates_test_path()
            )).from_string(template_str)
    html = template.render()
    soup = BeautifulSoup(html, 'html.parser')
    assert soup.body.contents[0].strip() == 'Test Body Content'
