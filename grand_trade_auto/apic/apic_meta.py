#!/usr/bin/env python3
"""
Holds the generic API Client meta-class that others will subclass.  Any other
shared API Client access code that needs to be accessed regardless of which API
can be implemented here so they have access when this is imported.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from abc import ABC, abstractmethod
import logging



logger = logging.getLogger(__name__)



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
      _apic_id (str): The id used as the section name in the API Client conf.
    """
    def __init__(self, env, apic_id, **kwargs):
        """
        Creates the API Client.

        Args:
          env (str): The run environment type valid for using this API Client.
          apic_id (str): The id used as the section name in the API Client conf.
        """
        self._env = env
        self._apic_id = apic_id

        if kwargs:
            logger.warning('Discarded excess kwargs provided to'
                    + f' {self.__class__.__name__}: {", ".join(kwargs.keys())}')



    @property
    def apic_id(self):
        """
        Gets the API Client ID for this API Client in a read-only fashion.

        Returns:
          _apic_id (str): The id used as the section name in the API Client
            conf.
        """
        return self._apic_id



    def matches_id_criteria(self, apic_id, env=None, provider=None):
        """
        Checks if this API Client is a match based on the provided criteria.

        Can provide more beyond minimum required parameters to explicitly
        overdefine.  No matter how minimally or overly defined inputs are, all
        non-None must match.

        Args:
          apic_id (str): The section ID of the API Client from the apics.conf
            file to check if this matches.
          env (str or None): The environment for which to check if this matches.
          provider (str or None): The provider to check if this matches.


        Returns:
          (bool): True if all provided criteria match; False otherwise.

        Raises:
          (AssertionError): Raised when an invalid combination of input arg
            criteria provided cannot guarantee a minimum level of definition.
        """
        assert apic_id is not None
        if apic_id != self._apic_id:
            return False
        if env is not None and env != self._env:
            return False
        if provider is not None and provider not in self.get_provider_names():
            return False
        return True



    @classmethod
    @abstractmethod
    def load_from_config(cls, apic_cp, apic_id):
        """
        Loads the API Client config for this API Client from the configparsers
        from files provided.

        Args:
          apic_cp (configparser): The full configparser from the API Client
            conf.
          apic_id (str): The ID name for this API Client as it appears as the
            section header in the apic_cp.

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
