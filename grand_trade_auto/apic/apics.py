#!/usr/bin/env python3
"""
The API Client access module.  This is intended to be the item accessed outside
of the API Client submodule/folder.

Module Attributes:
  _APIC (Apic<>): The handle to the API Client that will be used, where Apic<>
    is a subclass of Apic (e.g. Alpaca).
  _apics_loaded ({str: Apic<>})

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.apic import alpaca
from grand_trade_auto.general import config



_APIC = None    # Init'd later; but once init'd, should never change

_apics_loaded = {}



def load_and_set_main_apic_from_config(env, provider=None):
    """
    Loads the main API Client from config and sets it as the main handle open.

    Arg:
      env (str): The environment for which to load the API Client config.
      provider (str or None): The API Client provider type to be forced as the
        one to load; or None to simply take the first one found.

    Raises:
      (AssertionError): Raised if API Client already loaded or cannot be loaded.
    """
    # TEMP: debug
    provider = 'alpaca'
    alpaca.Alpaca.get_apic(env, provider)

    global _APIC                              # pylint: disable=global-statement
    assert _APIC is None, 'Cannot load API Clients: API Client already loaded.'
    apic = get_apic(env, provider)
    if apic is not None:
        _APIC = apic
        # TEMP: connecting here for testing purposes
        apic.connect()
    assert _APIC is not None, 'No valid API Client configuration found.'



def get_apic(env=None, provider=None, apic_id=None):
    """
    Gets the requested API Client.  Will return cached version if already
    loaded, otherwise will load.

    Minimum required is (`env`, `provider`) or (`apic_id`), but can provide
    more beyond one of those minimum required sets to explicitly overdefine.
    No matter how minimally or overly defined inputs are, all must match.  In
    the event that (`env`, `provider`) does not identify a unique API Client
    (e.g. multiple of same API Client for different accounts), it will return
    the first one found, which will be the first one loaded or the first one
    found in the conf file.

    TODO: Check for ambiguity in conf file and raise exception.

    Args:
      env (str or None): The environment for which to get the matching API
        Client.  Can be None if relying on `apic_id`.
      provider (str or None): The provider to get.  Can be None if relying
        on `apic_id`.
      apic_id (str or None): The section ID of the API Client from the
        apics.conf file.  Can be None if relying on other parameters.

    Returns:
      apic (Apic<> or None): Returns the API Client that matches the given
        criteria, loading from conf if required.  None if no matching API
        Client.

    Raises:
      (AssertionError): Raised when an invalid combination of input arg
        criteria provided cannot guarantee a minimum level of definition.
    """
    assert (env is not None and provider is not None) or apic_id is not None

    for apic in _apics_loaded.values():
        if apic.matches_id_criteria(env, provider, apic_id):
            return apic

    apic = _get_apic_from_config(env, provider, apic_id)
    if apic is not None:
        _apics_loaded[apic._cp_apic_id] = apic
    return apic



def _get_apic_from_config(env=None, provider=None, apic_id=None):
    """
    Loads the API Clients from the config file and sets the first one it finds
    to be the valid one to use.  Stores for later access.

    Minimum required is (`env`, `provider`) or (`apic_id`), but can provide
    more beyond one of those minimum required sets to explicitly overdefine.
    No matter how minimally or overly defined inputs are, all must match.  In
    the event that (`env`, `provider`) does not identify a unique API Client
    (e.g. multiple of same API Client for different accounts), it will return
    the first one found, which will be the first one loaded or the first one
    found in the conf file.

    TODO: Check for ambiguity in conf file and raise exception.

    Arg:
      env (str): The environment for which to load APIC config.  Can be None
        if relying on `apic_id`.
      provider (str or None): The provider for which to load API Client
        config.  Can be None if relying on `apic_id`.
      apic_id (str of None): The section ID of the API CLient from the
        apics.conf file to load.  Can be None if relying on other parameters.

    Returns:
      apic (Apic<> or None): The API Client loaded and created from
        the config file based on the provided criteria.  None if no match found.

    Raises:
      (AssertionError): Raised if API Client already loaded or cannot be loaded.
    """
    assert (env is not None and provider is not None) or apic_id is not None

    apic_cp = config.read_conf_file('apics.conf')
    secrets_cp = config.read_conf_file('.secrets.conf')
    apic_providers = {
        alpaca.Alpaca: alpaca.Alpaca.get_provider_names(),
    }

    for apic_sect_id in apic_cp.sections():
        if apic_id is not None and apic_id != apic_sect_id:
            continue
        if env is not None and env != apic_cp[apic_sect_id]['env'].strip():
            continue

        apic_class_sel = None
        for apic_class, provider_names in apic_providers.items():
            if apic_cp[apic_sect_id]['provider'].strip() in provider_names:
                apic_class_sel = apic_class
                break
        if apic_class_sel is None:
            continue

        if provider is not None \
                and provider not in apic_providers[apic_class_sel]:
            continue

        secrets_id = config.get_matching_secrets_id(secrets_cp, 'apic',
                apic_sect_id)

        apic = apic_class_sel.load_from_config(apic_cp,
                apic_sect_id, secrets_id)

        if apic is not None:
            return apic

    return None
