#!/usr/bin/env python3
"""
Main entry point for web backend via FastAPI.  Developed using uvicorn as ASGI.

Module Attributes:
  app (FastAPI): The FastAPI app handle.  Lowercase to make CLI invocation more
    convenient since it is case-sensitive.
  templates (Jinja2Templates): Loads and handles jinja2 templates in the
    provided dir.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from grand_trade_auto.general import dirs



app = FastAPI()
app.mount("/static",
        StaticFiles(directory=dirs.get_web_frontend_static_path()),
        name='static')
templates = Jinja2Templates(directory=dirs.get_jinja2_templates_path())



@app.get('/')
async def get_root(request: Request):
    """
    Gets the root web path's page's info.

    Args:
      request (Request): Contains fastapi request information for use/template.

    Returns:
      (TemplateResponse): At least contains the root index template filename
        from the template dir and a dict of data for root web path page.
    """
    context = {
        'request': request,
        'data': {
            'test_msg': 'Root page',
        },
    }
    return templates.TemplateResponse('root_index.html', context)
