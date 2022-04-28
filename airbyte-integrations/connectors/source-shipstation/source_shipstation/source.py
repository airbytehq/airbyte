from typing import Any, List, Mapping, Tuple

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from source_shipstation.streams import Customers, Fulfillments, Products, Orders, Stores, Warehouses


class SourceShipstation(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        auth = HTTPBasicAuth(username=config["api_key"], password=config["api_secret"])
        try:
            Fulfillments(authenticator=auth)
            connection = True, None
        except Exception as e:
            connection = False, e

        return connection

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        auth = HTTPBasicAuth(username=config["api_key"], password=config['api_secret'])
        return [
            Customers(authenticator=auth),
            Fulfillments(authenticator=auth),
            Products(authenticator=auth),
            Orders(authenticator=auth),
            Stores(authenticator=auth),
            Warehouses(authenticator=auth)
        ]
