#!/usr/bin/env python3
"""
Temporary main file to enable some package testing / dev until the real main
entry modules are implemented.

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from grand_trade_auto.database import databases



logging.basicConfig(level=logging.DEBUG)



def main():
    """
    Launches the main app.
    """
    databases.load_and_set_main_database_from_config('test')



if __name__ == '__main__':
    main()
