#!/usr/bin/env python3
"""
Temporary main file to enable some package testing / dev until the real main
entry modules are implemented.

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.database import databases
from grand_trade_auto.general import config



def main():
    """
    Launches the main app.
    """
    config.init_logger('DEBUG')
    databases.load_and_set_main_database_from_config('test')



if __name__ == '__main__':
    main()
