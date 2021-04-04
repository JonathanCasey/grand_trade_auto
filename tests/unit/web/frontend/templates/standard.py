#!/usr/bin/env python3
"""
Common tests that should apply to multiple templates in order to standardize
certain web page elements.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from bs4 import BeautifulSoup



def are_style_sheets_scripts_present(rendered_html):
    """
    Checks that the overall style sheets and scripts are present in the rendered
    html.

    Args:
      rendered_html (str): The rendered html for the page.

    Raises:
      (Exception): Will raise exceptions for failed tests.
    """
    soup = BeautifulSoup(rendered_html, 'html.parser')
    link_tags = soup.head.find_all('link', {'rel': 'stylesheet'})

    semantic_stylesheet_found = False
    semantic_stylesheet_url = \
            'https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.css'
    for link_tag in link_tags:
        if 'href' not in link_tag.attrs:
            continue

        if link_tag['href'] == semantic_stylesheet_url:
            semantic_stylesheet_found = True
            break

    assert semantic_stylesheet_found, \
            'Semantic UI Stylesheet missing from HTML head.'


    script_tags = soup.head.find_all('script')

    semantic_min_js_found = False
    semantic_min_js_url = \
            'https://cdn.jsdelivr.net/npm/semantic-ui@2.4.2/dist/semantic.min.js'
    for script_tag in script_tags:
        if 'src' not in script_tag.attrs:
            continue

        if script_tag['src'] == semantic_min_js_url:
            semantic_min_js_found = True
            break

    assert semantic_min_js_found, \
            'Semantic UI Min JS script missing from HTML head.'
