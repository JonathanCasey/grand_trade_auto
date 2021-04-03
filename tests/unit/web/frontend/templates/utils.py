#!/usr/bin/env python3
"""
Common utility functions used in jinja2 frontend template testing.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import jinja2

from grand_trade_auto.general import dirs



def render(filename, context):
    """
    Renders a jinja2 template based on the provided template filename and the
    context data provided.

    Args:
      filename (str): Name of the jinja2 template to render.
      context ({str:str/int/etc}): The context data to populate into the
        template fields in the template.

    Returns:
      (str): Rendered html output resulting from this template file and the
        provided context data.
    """
    return jinja2.Environment(
                loader=jinja2.FileSystemLoader(dirs.get_jinja2_templates_path())
            ).get_template(filename).render(context)
