#!/usr/bin/env python3
"""
Alpaca functionality to implement the generic interface components defined
by the metaclass.

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

from grand_trade_auto.broker import broker_meta



logger = logging.getLogger(__name__)



class BrokerAlpaca(broker_meta.BrokerMeta):
    """
    The Alpaca broker functionality.

    Class Attributes:
      base_urls ({str:str}): The base URLs, keyed by trade domain.

    Instance Attributes:
      N/A
    """
    base_urls = {
        'live': 'https://api.alpaca.markets',
        'paper': 'https://paper-api.alpaca.markets',
    }



    def __init__(self, trade_domain, cp_broker_id, cp_secrets_id):
        """
        Creates the broker handle.
        """
        self.trade_domain = trade_domain
        self.cp_broker_id = cp_broker_id
        self.cp_secrets_id = cp_secrets_id

        self.base_url = self.base_urls[trade_domain]

        super().__init__()



    @classmethod
    def load_from_config(cls, broker_cp, broker_id, secrets_cp, secrets_id):
        """
        Loads the broker config for this broker from the configparsers
        from files provided.

        Args:
          broker_cp (configparser): The full configparser from the broker conf.
          broker_id (str): The ID name for this broker as it appears as the
            section header in the broker_cp.
          secrets_cp (configparser): The full configparser from the secrets
            conf.
          secrets_id (str): The ID name for this broker's secrets as it
            appears as the section header in the secrets_cp.

        Returns:
          broker_handle (BrokerMeta<>): The BrokerMeta<> object created and
            loaded from config, where BrokerMeta<> is a subclass of
            BrokerMeta (e.g. BrokerAlpaca).
        """
        kwargs = {}

        kwargs['trade_domain'] = broker_cp[broker_id]['trade domain']
        kwargs['cp_broker_id'] = broker_id
        kwargs['cp_secrets_id'] = secrets_id

        broker_handle = BrokerAlpaca(**kwargs)
        return broker_handle



    @classmethod
    def get_type_names(cls):
        """
        Get the list of names that can be used as the 'type' in the broker
        conf to identify this broker.

        Returns:
          ([str]): A list of names that are valid to use for this broker type.
        """
        return ['alpaca', 'apca']
