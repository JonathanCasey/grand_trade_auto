#!/usr/bin/env python3
"""
Alpha Vantage functionality to implement the generic interface components
defined by the metaclass.

Module Attributes:
  N/A

(C) Copyright 2021 Jonathan Casey.  All Rights Reserved Worldwide.
"""
from enum import Enum
import requests

from grand_trade_auto.apic import apic_meta
from grand_trade_auto.general import config



class DataType(Enum):
    """
    """
    CSV = 'csv'
    JSON = 'json'



class AlphavantageApic(apic_meta.Apic):
    """
    The Alpha Vantage broker API Client functionality.

    Class Attributes:
      N/A

    Instance Attributes:
      _api_key (str): The API key used for authentication.

      [inherited from Apic]:
        _env (str): The run environment type valid for using this API Client.
        _apic_id (str): The id used as the section name in the API Client conf.
    """
    def __init__(self, api_key, **kwargs):
        """
        Creates the Alpha Vantage API client.

        Args:
          api_key (str): The secret key used for authentication.

          See parent(s) for required kwargs.
        """
        super().__init__(**kwargs)
        self._api_key = api_key



    @classmethod
    def load_from_config(cls, apic_cp, apic_id):
        """
        Loads the Alpha Vantage config from the configparsers from files
        provided.

        Args:
          apic_cp (configparser): The full configparser from the API Client
            conf.
          apic_id (str): The ID name for this API Client as it appears as the
            section header in the apic_cp.

        Returns:
          alphav (Alphavantage): The Alpha Vantage object created and loaded
            from config.
        """
        apic_cp = config.read_conf_file('apics.conf')
        secrets_cp = config.read_conf_file('.secrets.conf')
        secrets_id = config.get_matching_secrets_id(secrets_cp, 'apic', apic_id)

        kwargs = {}
        kwargs['env'] = apic_cp[apic_id]['env'].strip()
        kwargs['apic_id'] = apic_id

        kwargs['api_key'] = secrets_cp.get(secrets_id, 'api key', fallback=None)

        alphav = cls(**kwargs)
        return alphav



    @classmethod
    def get_provider_names(cls):
        """
        Get the list of names that can be used as the 'provider' in the API
        Client conf to identify this API Client.

        Returns:
          ([str]): A list of names that are valid to use for this API Client
            provider.
        """
        return ['alpha vantage', 'alphavantage', 'alphav', 'av']



    def connect(self):
        """
        Connects to the API provider's servers.
        """
        # No connection to maintain
        return



    def _call_api(self, url, return_type):
        """
        """
        if return_type is DataType.CSV:
            with requests.Session() as s:
                download = s.get(url)
                data = download.content.decode('utf-8')
        elif return_type is DataType.JSON:
            request = requests.get(url)
            data = request.json()
        # TODO (Future/as it comes up): What are the errors??
        return data, None


    @staticmethod
    def _convert_params_to_url_str(params):
        """
        """
        return '&'.join([f'{k}={v}' for k, v in params.items()])


    def call_api(self, base_url, params, return_type=None, add_secrets=True):
        """
        """
        if add_secrets:
            params['apikey'] = self._api_key
        url = base_url + self._convert_params_to_url_str(params)
        if 'datatype' in params:
            if return_type is not None \
                    and return_type != DataType(params['datatype']):
                raise Exception('Conflicting return types...')
            return_type = params['datatype']
        if return_type is None:
            raise Exception('datatype in params or return_type arg required')

        return self._call_api(url, return_type)
