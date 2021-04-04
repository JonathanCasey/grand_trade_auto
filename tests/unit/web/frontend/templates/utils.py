#!/usr/bin/env python3
"""
Common utility functions used in jinja2 frontend template testing.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import os
import os.path
import re

import jinja2

from grand_trade_auto.general import dirs



def render(filename, context):
    """
    Renders a jinja2 template based on the provided template filename and the
    context data provided.

    Will do so as true to the original template as possible; but if non-jinja2
    elements used (e.g. `url_for()` from fastapi), this will sanitize the
    template before rendering.  These elements will NOT be valid to test, but it
    will allow rest of the rendering to be tested.

    Args:
      filename (str): Name of the jinja2 template to render.
      context ({str:str/int/etc}): The context data to populate into the
        template fields in the template.

    Returns:
      rendered_html (str): Rendered html output resulting from this template
        file and the provided context data.
    """
    sanitized_filename = sanitize_non_jinja2(filename)
    if sanitized_filename:
        dir_to_load = get_sanitized_jinja2_templates_test_path()
        filename_to_load = sanitized_filename
    else:
        dir_to_load = dirs.get_jinja2_templates_path()
        filename_to_load = filename

    try:
        rendered_html = jinja2.Environment(
                    loader=jinja2.FileSystemLoader(dir_to_load)
                ).get_template(filename_to_load).render(context)
    # Let exception pass through to test case caller if raised
    finally:
        if sanitized_filename:
            sanitized_filepath = os.path.join(
                    get_sanitized_jinja2_templates_test_path(),
                    sanitized_filename)
            os.remove(sanitized_filepath)

    return rendered_html



def sanitize_non_jinja2(filename):
    """
    Replaces non-jinja2 elements with default text to enable rendering.

    Contents of sanitized regions NOT guaranteed to be relevant at all to what
    they originally contained, so it is not valid to check these regions at all.
    The purpose is to allow rendering to succeed so the other portions can be
    checked.

    Currently sanitizing:
      - url_for()   # fastapi

    Args:
      filename (str): Name of the jinja2 template to sanitize.

    Returns:
      sanitized_filename (str or None): Name of the sanitized filename to use
        from the directory of sanitized templates for test.  None if no changes
        and original can be used.
    """
    sanitized_filename = None

    url_for_ptn = re.compile(r'{{\s*url_for\([^\)]*\)\s*}}', re.IGNORECASE)

    orig_filepath = os.path.join(dirs.get_jinja2_templates_path(), filename)
    with open(orig_filepath, 'r') as f:
        orig_text = f.read()

    sanitized_text = orig_text
    sanitized_text = url_for_ptn.sub('sanitized__url_for', sanitized_text)

    if orig_text != sanitized_text:
        sanitized_filename = f'tmp_sanitized__{filename}'
        sanitized_filepath = os.path.join(
                get_sanitized_jinja2_templates_test_path(), sanitized_filename)
        with open(sanitized_filepath, 'w') as f:
            f.write(sanitized_text)

    return sanitized_filename



def get_sanitized_jinja2_templates_test_path():
    """
    Get the path to sanitized jinja2 templates used for test.

    Returns:
      (os.path): Path to dir that stores sanitized jinja2 templates for test.
    """
    this_script_dir = os.path.dirname(os.path.realpath(__file__))
    return this_script_dir
