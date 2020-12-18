#!/usr/bin/env python3
"""
Temporary main file to enable some package testing / dev until the real main
entry modules are implemented.

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging
import logging.config
import os.path

from grand_trade_auto.database import databases
from grand_trade_auto.general import dirs



logging.addLevelName(99, 'DISABLED')
logging.config.fileConfig(os.path.join(dirs.get_conf_path(), 'logger.conf'),
        disable_existing_loggers=False)



def main():
    """
    Launches the main app.
    """

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    databases.load_and_set_main_database_from_config('test')



if __name__ == '__main__':
    main()
