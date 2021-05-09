#!/usr/bin/env python3
"""
Holds the generic API Client meta-class that others will subclass.  Any other
shared API Client access code that needs to be accessed regardless of which API
can be implemented here so they have access when this is imported.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from abc import ABC, abstractmethod



class Apic(ABC):
    """
    The abstract class for all API Client functionality.  Each API Client
    provider will subclass this, but externally will likely only call the
    generic methods defined here to unify the interface.

    This serves as a base class for other API Client use types, so will consume
    any final kwargs.

    Class Attributes:
      N/A

    Instance Attributes:
      _env (str): The run environment type valid for using this API Client.
      _cp_apic_id (str): The id used as the section name in the API Client
        conf.  Will be used for loading credentials on-demand.
      _cp_secrets_id (str): The id used as the section name in the secrets
        conf.  Will be used for loading credentials on-demand.
    """
    @abstractmethod
    def __init__(self, env, cp_apic_id, cp_secrets_id, **kwargs):
        """
        Creates the API Client.

        Args:
          env (str): The run environment type valid for using this API Client.
          cp_apic_id (str): The id used as the section name in the API Client
            conf.  Will be used for loading credentials on-demand.
          cp_secrets_id (str): The id used as the section name in the secrets
            conf.  Will be used for loading credentials on-demand.
        """
        self._env = env
        self._cp_apic_id = cp_apic_id
        self._cp_secrets_id = cp_secrets_id



    @classmethod
    @abstractmethod
    def load_from_config(cls, apic_cp, apic_id, secrets_id):
        """
        Loads the API Client config for this API Client from the configparsers
        from files provided.

        Args:
          apic_cp (configparser): The full configparser from the API Client
            conf.
          apic_id (str): The ID name for this API Client as it appears as the
            section header in the apic_cp.
          secrets_id (str): The ID name for this API Client's secrets as it
            appears as the section header in the secrets_cp.

        Returns:
          apic (Apic<>): The Apic<> object created and loaded from config, where
            Apic<> is a subclass of Apic (e.g. Alpaca).
        """



    @classmethod
    @abstractmethod
    def get_provider_names(cls):
        """
        Get the list of names that can be used as the 'provider' in the API
        Client conf to identify this API Client.

        Returns:
          ([str]): A list of names that are valid to use for this API Client
            provider.
        """



    @abstractmethod
    def connect(self):
        """
        Connects to the API provider's servers.
        """
