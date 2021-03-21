#!/usr/bin/env python3
"""This module lists all user defined exceptions for import to the modules
that need them.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""



class EmailConnectionError(Exception):
    """
    Raised when an email fails to send for a connection-related reason.
    """
