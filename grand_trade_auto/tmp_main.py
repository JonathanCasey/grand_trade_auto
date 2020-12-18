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
from grand_trade_auto.general import config



if __name__ == '__main__':
    logger = logging.getLogger('grand_trade_auto.tmp_main')
else:
    logger = logging.getLogger(__name__)



def main():
    """
    Launches the main app.
    """
    config.init_logger('DEBUG')
    databases.load_and_set_main_database_from_config('test')
    logger.error('error message')
    logger.warning('warning message')
    logger.log(99, 'disabled message?')



if __name__ == '__main__':
    main()
