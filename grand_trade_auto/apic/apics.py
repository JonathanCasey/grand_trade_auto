#!/usr/bin/env python3
"""
The API Client access module.  This is intended to be the item accessed outside
of the API Client submodule/folder.

Module Attributes:
  _APIC_PROVIDERS ((Class<Apic<>>)): All API Client classes supported.
  _apics_loaded ({str: Apic<>}): The API Clients loaded and cached, keyed by
    their APIC IDs (i.e. conf section IDs).

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from grand_trade_auto.apic import alpaca
from grand_trade_auto.general import config



_APIC_PROVIDERS = (
    alpaca.Alpaca,
)

_apics_loaded = {}



def get_apic(apic_id, env=None):
    """
    Gets the requested API Client.  Will return cached version if already
    loaded, otherwise will load and cache.

    Args:
      apic_id (str): The section ID of the API Client from the apics.conf file.
      env (str or None): The environment for which this API Client is valid.
        Optional - can be used to be protect against incorrect access.

    Returns:
      apic (Apic<> or None): Returns the API Client that matches the given
        criteria, loading from conf if required.  None if no matching API
        Client.

    Raises:
      (AssertionError): Raised when an invalid combination of input arg
        criteria provided cannot guarantee a minimum level of definition.
    """
    assert apic_id is not None

    if apic_id in _apics_loaded:
        if _apics_loaded[apic_id].matches_id_criteria(apic_id, env):
            return _apics_loaded[apic_id]

    apic = _get_apic_from_config(apic_id, env)
    if apic is not None:
        _apics_loaded[apic_id] = apic
    return apic



def _get_apic_from_config(apic_id, env=None):
    """
    Loads the specified API Client from the config file.

    Arg:
      apic_id (str): The section ID of the API Client from the apics.conf file
        to load.
      env (str or None): The environment for which this API Client is valid.
        Optional - can be used to be protect against incorrect access.

    Returns:
      apic (Apic<> or None): The API Client loaded and created from the config
        file based on the provided criteria.  None if no match found.

    Raises:
      (AssertionError): Raised if API Client cannot be loaded.
    """
    assert apic_id is not None

    apic_cp = config.read_conf_file('apics.conf')
    secrets_cp = config.read_conf_file('.secrets.conf')

    if apic_id not in apic_cp.sections():
        return None

    if env is not None and env != apic_cp[apic_id]['env'].strip():
        return None

    apic_provider_sel = None
    for apic_provider in _APIC_PROVIDERS:
        if apic_cp[apic_id]['provider'].strip() \
                in apic_provider.get_provider_names():
            apic_provider_sel = apic_provider
            break

    if apic_provider_sel is None:
        return None

    secrets_id = config.get_matching_secrets_id(secrets_cp, 'apic', apic_id)
    apic = apic_provider_sel.load_from_config(apic_cp, apic_id, secrets_id)
    return apic
