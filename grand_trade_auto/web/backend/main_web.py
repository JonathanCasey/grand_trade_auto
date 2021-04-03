#!/usr/bin/env python3
"""
Main entry point for web backend via FastAPI.  Developed using uvicorn as ASGI.

Module Attributes:
  app (FastAPI): The FastAPI app handle.  Lowercase to make CLI invocation more
    convenient since it is case-sensitive.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from fastapi import FastAPI



app = FastAPI()



@app.get('/')
async def get_root():
    """
    Gets the root web path's page's info.

    Returns:
      ({str}:{str/int/etc}): A JSON dict of data for root web path page.
    """
    return {'msg': 'Root page'}
