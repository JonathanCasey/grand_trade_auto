#!/usr/bin/env python3
"""
Holds the generic broker meta-class that others will subclass.  Any other
shared broker code that needs to be accessed by all brokers can be
implemented here so they have access when this is imported.

Module Attributes:
  N/A

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from abc import ABC, abstractmethod

from grand_trade_auto.apic import apic_meta



class Broker(apic_meta.Apic, ABC):
    """
    The abstract class for all broker functionality.  Each broker type will
    subclass this, but externally will likely only call the generic methods
    defined here to unify the interface.

    Class Attributes:
      N/A

    Instance Attributes:
      [inherited from ApicMeta]:
        _env (str): The run environment type valid for using this broker.
        _cp_broker_id (str): The id used as the section name in the API Client
          conf.  Will be used for loading credentials on-demand.
        _cp_secrets_id (str): The id used as the section name in the secrets
          conf.  Will be used for loading credentials on-demand.
    """
    @abstractmethod
    def __init__(self, **kwargs):
        """
        Creates the broker.

        Args:
          See parent(s) for required kwargs.
        """
        super().__init__(**kwargs)
