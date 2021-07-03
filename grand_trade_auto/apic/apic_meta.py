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
      _cp_apic_id (str): The id used as the section name in the API Client
        conf.  Will be used for loading credentials on-demand.
      _cp_secrets_id (str): The id used as the section name in the secrets
        conf.  Will be used for loading credentials on-demand.
    """
    apics_loaded = None


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

        if kwargs:
            logger.warning('Discarded excess kwargs provided to'
                    + f' {self.__class__.__name__}: {", ".join(kwargs.keys())}')



    @classmethod
    @abstractmethod
    def get_apic(cls, env=None, provider=None, apic_id=None):
        """
        Gets the requested API Client.  Will return cached version if already
        loaded, otherwise will load.

        Minimum required is (`env`, `provider`) or (`apic_id`), but can provide
        more beyond one of those minimum required sets to explicitly overdefine.
        No matter how minimally or overly defined inputs are, all must match.
        In the event that (`env`, `provider`) does not identify a unique API
        Client (e.g. multiple of same API Client for different accounts), it
        will return the first one found, which will be the first one loaded or
        the first one found in the conf file.

        Abstract so cannot be called via this meta class.

        TODO: Check for ambiguity in conf file and raise exception.

        Args:
          env (str or None): The environment for which to get the matching API
            Client.  Can be None if relying on `apic_id`.
          provider (str or None): The provider to get.  Can be None if relying
            on `apic_id`.
          apic_id (str or None): The section ID of the API Client from the
            apics.conf file.  Can be None if relying on other parameters.

        Returns:
          apic (Apic<> or None): Returns the API Client that matches the
            given criteria, loading from conf if required.  None if no matching
            API Client.

        Raises:
          (AssertionError): Raised when an invalid combination of input arg
            criteria provided cannot guarantee a minimum level of definition.
        """
        assert (env is not None and provider is not None) or apic_id is not None

        if cls.apics_loaded is None:
            cls.apics_loaded = {}
            # TEMP: debug
            print(cls.__name__)

        apics_to_check = []
        if apic_id is not None:
            if apic_id in cls.apics_loaded:
                apics_to_check = [cls.apics_loaded[apic_id]]
        else:
            apics_to_check = cls.apics_loaded.values()

        for apic in apics_to_check:
            if apic.matches_id_criteria(env, provider, apic_id):
                return apic

        # TODO: Load from config

        return None



    def matches_id_criteria(self, env=None, provider=None, apic_id=None):
        """
        Checks if this API Client is a match based on the provided criteria.

        Minimum required is (`env`, `provider`) or (`apic_id`), but can provide
        more beyond one of those minimum required sets to explicitly overdefine.
        No matter how minimally or overly defined inputs are, all must match.

        Args:
          env (str or None): The environment for which to check if this matches.
            Can be None if relying on `apic_id`.
          provider (str or None): The provider to check if this matches.  Can be
            None if relying on `apic_id`.
          apic_id (str or None): The section ID of the API Client from the
            apics.conf file to check if this matches.  Can be None if relying
            on other parameters.

        Returns:
          (bool): True if all provided criteria match; False otherwise.

        Raises:
          (AssertionError): Raised when an invalid combination of input arg
            criteria provided cannot guarantee a minimum level of definition.
        """
        assert (env is not None and provider is not None) \
            or apic_id is not None
        if apic_id is not None and provider != self._cp_apic_id:
            return False
        if env is not None and env != self._env:
            return False
        if provider is not None and provider not in self.get_provider_names():
            return False
        return True



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
