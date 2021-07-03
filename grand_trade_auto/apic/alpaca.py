#!/usr/bin/env python3
"""
Alpaca functionality to implement the generic interface components defined
by the metaclass.

Module Attributes:
  logger (Logger): Logger for this module.

(C) Copyright 2020 Jonathan Casey.  All Rights Reserved Worldwide.
"""
import logging

import alpaca_trade_api as tradeapi

from grand_trade_auto.broker import broker_meta
from grand_trade_auto.datafeed import datafeed_meta
from grand_trade_auto.general import config



logger = logging.getLogger(__name__)



class Alpaca(broker_meta.Broker, datafeed_meta.Datafeed):
    """
    The Alpaca broker API Client functionality.

    Class Attributes:
      _base_urls ({str:str}): The base URLs, keyed by trade domain.

    Instance Attributes:
      _trade_domain (str): The domain for trading (live or paper).

      _base_url (str): The base url to use based on trade domain.
      _rest_api (REST): The cached rest API connection; or None if not connected
        and cached.
      _stream_conn (StreamConn): The cached stream socket connection; or None if
        not connected and cached.

      [inherited from Apic]:
        _env (str): The run environment type valid for using this API Client.
        _cp_apic_id (str): The id used as the section name in the API Client
          conf.  Will be used for loading credentials on-demand.
        _cp_secrets_id (str): The id used as the section name in the secrets
          conf.  Will be used for loading credentials on-demand.
    """
    _base_urls = {
        'live': 'https://api.alpaca.markets',
        'paper': 'https://paper-api.alpaca.markets',
    }



    def __init__(self, trade_domain, **kwargs):
        """
        Creates the Alpaca API client.

        Args:
          trade_domain (str): The domain for trading (live or paper).

          See parent(s) for required kwargs.
        """
        super().__init__(**kwargs)
        self._trade_domain = trade_domain

        self._base_url = self._base_urls[trade_domain]

        self._rest_api = None
        self._stream_conn = None



    @classmethod
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
        super().get_apic(env, provider, apic_id)



    @classmethod
    def load_from_config(cls, apic_cp, apic_id, secrets_id):
        """
        Loads the Alpaca config from the configparsers from files provided.

        Args:
          apic_cp (configparser): The full configparser from the API Client
            conf.
          apic_id (str): The ID name for this API Client as it appears as the
            section header in the apic_cp.
          secrets_id (str): The ID name for this API Client's secrets as it
            appears as the section header in the secrets_cp.

        Returns:
          alpaca (Alpaca): The Alpaca object created and loaded from config.
        """
        kwargs = {}

        kwargs['env'] = apic_cp[apic_id]['env'].strip()
        kwargs['cp_apic_id'] = apic_id
        kwargs['cp_secrets_id'] = secrets_id
        kwargs['trade_domain'] = apic_cp[apic_id]['trade domain'].strip()

        alpaca = Alpaca(**kwargs)
        return alpaca



    @classmethod
    def get_provider_names(cls):
        """
        Get the list of names that can be used as the 'provider' in the API
        Client conf to identify this API Client.

        Returns:
          ([str]): A list of names that are valid to use for this API Client
            provider.
        """
        return ['alpaca', 'apca']



    def connect(self):
        """
        Connects to the API provider's servers.
        """
        self._connect()



    def _connect(self, interface='rest'):
        """
        Connects via the desired interface.  Connection caching is handled by
        the API module.

        Args:
          interface (str): Specify whether to connect to the 'rest' API; or to
            use the 'stream' connection.

        Raises:
          (NotImplementedError): 'stream' is not yet implemented.
          (ValueError): interface is something other than 'rest', 'stream'.
          (ConnectionRefusedError): Attempted and failed to connect.
        """
        if interface == 'rest' and self._rest_api is not None:
            return
        if interface == 'stream' and self._stream_conn is not None:
            return

        apic_cp = config.read_conf_file('apics.conf')
        secrets_cp = config.read_conf_file('.secrets.conf')

        kwargs = {
            'base_url': self._base_url,
        }
        kwargs['key_id'] = apic_cp.get(self._cp_apic_id, 'api key id',
                fallback=None)
        kwargs['key_id'] = secrets_cp.get(self._cp_secrets_id, 'api key id',
                fallback=kwargs['key_id'])
        kwargs['secret_key'] = secrets_cp.get(self._cp_secrets_id, 'secret key',
                fallback=None)

        if interface == 'rest':
            try:
                self._rest_api = tradeapi.REST(**kwargs)
                account = self._rest_api.get_account()
            except ValueError as ex:
                msg = 'Unable to connect to Alpaca.' \
                        + f'  API Error: {str(ex)}'
                logger.critical(msg)
                raise ConnectionRefusedError(msg) from ex
            except tradeapi.rest.APIError as ex:
                msg = 'Unable to connect to Alpaca.' \
                        + f'  API Error: {str(ex)}'
                logger.critical(msg)
                raise ConnectionRefusedError(msg) from ex

            if account.status == 'ACTIVE':
                logger.info('Established connection to Alpaca via REST.')
            else:
                msg = 'Unable to connect to Alpaca.' \
                        + f'  Account status: {account.status}'
                logger.critical(msg)
                raise ConnectionRefusedError(msg)

        elif interface == 'stream':
            raise NotImplementedError(
                    'Stream connection not implemented for Alpaca')
        else:
            raise ValueError('Invalid interface for Alpaca'
                    + f' -- must be "rest" or "stream"; got {interface}')
