#!/usr/bin/env python3
"""
Temporary main file to enable some package testing / dev until the real main
entry modules are implemented.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from grand_trade_auto.broker import brokers
from grand_trade_auto.database import databases
from grand_trade_auto.general import config
from grand_trade_auto.general import email_report



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
    brokers.load_and_set_main_broker_from_config('test')
    email_report.send_email('Test GTA email', 'From grand_trade_auto project.')



if __name__ == '__main__':
    main()
