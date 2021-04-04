#!/usr/bin/env python3
"""
Common tests that should apply to multiple modules in order to standardize
certain web page elements.

This will include elements that really test frontend elements but are not
rendered correctly without fastapi.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import re

from bs4 import BeautifulSoup



def is_favicon_present(rendered_html):
    """
    Checks that the favicon is present in the rendered html.

    Args:
      rendered_html (str): The rendered html for the page.

    Returns:
      success (bool): True if all checks passed; False otherwise.

    Raises:
      (Exception): Will raise exceptions for failed tests.
    """
    success = True
    favicon_found = False

    soup = BeautifulSoup(rendered_html, 'html.parser')
    favicon_attrs = {
        'rel': 'icon',
        'sizes': '64x64',
    }
    link_tags = soup.head.find_all('link', favicon_attrs)

    favicon_href_ptn = re.compile(r'^http://[^/]+/static/images/favicon\.ico$')

    for link_tag in link_tags:
        if 'href' not in link_tag.attrs:
            continue

        if favicon_href_ptn.match(link_tag['href']) is not None:
            favicon_found = True
            break

    assert favicon_found

    if not favicon_found:
        success = False

    return success
