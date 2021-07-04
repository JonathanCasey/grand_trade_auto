#!/usr/bin/env python3
"""
Temporary main file to enable some package testing / dev until the real main
entry modules are implemented.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from grand_trade_auto.apic import apics
from grand_trade_auto.database import databases
from grand_trade_auto.general import config
from grand_trade_auto.general import email_report
from grand_trade_auto.general.exceptions import *   # pylint: disable=wildcard-import, unused-wildcard-import



if __name__ == '__main__':                                  # Ignored by CodeCov
    # Since no unit testing here, code kept at absolute minimum
    logger = logging.getLogger('grand_trade_auto.tmp_main')
else:
    logger = logging.getLogger(__name__)



def main():
    """
    Launches the main app.
    """
    config.init_logger('DEBUG')
    db = databases.get_database('postgres-test', 'test')
    db.create_db()
    apic = apics.get_apic('alpaca-test', 'test')
    apic.connect()
    try:
        email_report.send_email('Test GTA email', 'From grand_trade_auto.')
    except EmailConfigError:
        logger.warning('Email config could not be loaded.  Skipping.')
    except EmailConnectionError:
        logger.warning('Email could not be sent (connection error).  Skipping.')



if __name__ == '__main__':                                  # Ignored by CodeCov
    # Since no unit testing here, code kept at absolute minimum
    main()
