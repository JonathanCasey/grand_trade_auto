#!/usr/bin/env python3
"""
Common utility functions used in jinja2 frontend template testing.

Module Attributes:
  SANITIZED_FILENAME_TEMAPLTE (Template): String template for filename change
    to create sanitized filename from original filename.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import os
import os.path
import re
from string import Template

import jinja2

from grand_trade_auto.general import dirs



SANITIZED_FILENAME_TEMAPLTE = Template('tmp_sanitized__$filename')



def render_sanitized(filename, context=None):
    """
    Renders a jinja2 template based on the provided template filename and the
    context data provided.

    Will do so as true to the original template as possible; but if non-jinja2
    elements used (e.g. `url_for()` from fastapi), this will sanitize the
    template before rendering.  These elements will NOT be valid to test, but it
    will allow rest of the rendering to be tested.

    Args:
      filename (str): Name of the jinja2 template to render.
      context ({str:str/int/etc} or None): The context data to populate into the
        template fields in the template.  Can be omitted if no context needed.

    Returns:
      rendered_html (str): Rendered html output resulting from this template
        file and the provided context data.
    """
    if context is None:
        context = {}

    sanitized_filename = SANITIZED_FILENAME_TEMAPLTE.substitute(
            filename=filename)
    dir_for_sanitized = get_sanitized_jinja2_templates_test_path()

    rendered_html = jinja2.Environment(
                loader=jinja2.FileSystemLoader(dir_for_sanitized)
            ).get_template(sanitized_filename).render(context)

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
      sanitized_filename (str): Name of the sanitized filename to use from the
        directory of sanitized templates for test.  File saved with new name
        even if identical.
    """
    url_for_ptn = re.compile(r'{{\s*url_for\([^\)]*\)\s*}}', re.IGNORECASE)

    orig_filepath = os.path.join(dirs.get_jinja2_templates_path(), filename)
    with open(orig_filepath, 'r') as f:
        orig_text = f.read()

    sanitized_text = orig_text
    sanitized_text = url_for_ptn.sub('sanitized__url_for', sanitized_text)

    sanitized_filename = SANITIZED_FILENAME_TEMAPLTE.substitute(
            filename=filename)
    sanitized_filepath = os.path.join(
            get_sanitized_jinja2_templates_test_path(), sanitized_filename)
    with open(sanitized_filepath, 'w') as f:
        f.write(sanitized_text)

    return sanitized_filename



def sub_sanitized_jinja2_extends(filename=None, sanitized_filename=None):
    """
    Substitutes any "extends" syntax in jinja2 templates with the sanitized
    filename versions of those templates.  Assumes the sanitized template
    already exists.

    Args:
      filename (str or None): The original template filename.  Must be skipped
        if `sanitized_filename` provided instead.
      sanitized_filename (str or None): The sanitized template filename.  Must
        be skipped if original `filename` provided instead.
    """
    assert (filename is None and sanitized_filename is not None) \
            or (filename is not None and sanitized_filename is None)
    if sanitized_filename is None:
        sanitized_filename = SANITIZED_FILENAME_TEMAPLTE.substitute(
                filename=filename)

    extends_ptn = re.compile(r'{%\s+extends\s+"(?P<filename>[^"]+)"\s+%}',
            re.IGNORECASE)

    sanitized_filepath = os.path.join(
            get_sanitized_jinja2_templates_test_path(), sanitized_filename)

    with open(sanitized_filepath, 'r') as f:
        orig_text = f.read()

    new_text = orig_text
    for match in extends_ptn.finditer(new_text):
        new_filename = SANITIZED_FILENAME_TEMAPLTE.substitute(
                filename=match.group('filename'))

        new_text = new_text[:match.start('filename')] \
                + new_filename \
                + new_text[match.end('filename'):]

    with open(sanitized_filepath, 'w') as f:
        f.write(new_text)



def get_sanitized_jinja2_templates_test_path():
    """
    Get the path to sanitized jinja2 templates used for test.

    Returns:
      (os.path): Path to dir that stores sanitized jinja2 templates for test.
    """
    this_script_dir = os.path.dirname(os.path.realpath(__file__))
    return this_script_dir
