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



class BrokerMeta(ABC):
    """
    The abstract class for all broker functionality.  Each broker type will
    subclass this, but externally will likely only call the generic methods
    defined here to unify the interface.

    Class Attributes:
      N/A

    Instance Attributes:
      N/A
    """
    @abstractmethod
    def __init__(self):
        """
        Creates the broker handle.
        """



    @classmethod
    @abstractmethod
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



    @classmethod
    @abstractmethod
    def get_type_names(cls):
        """
        Get the list of names that can be used as the 'type' in the broker
        conf to identify this broker.

        Returns:
          ([str]): A list of names that are valid to use for this broker type.
        """



    @abstractmethod
    def connect(self):
        """
        Connects to the broker's servers.
        """
