#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, List, Mapping, Tuple

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator

from source_shipstation.streams import Customers, Fulfillments, Products, Orders, Stores, Warehouses

"""
TODO: Most comments in this class are instructive and should be deleted after the source is implemented.

This file provides a stubbed example of how to use the Airbyte CDK to develop both a source connector which supports full refresh or and an
incremental syncs from an HTTP API.

The various TODOs are both implementation hints and steps - fulfilling all the TODOs should be sufficient to implement one basic and one incremental
stream from a source. This pattern is the same one used by Airbyte internally to implement connectors.

The approach here is not authoritative, and devs are free to use their own judgement.

There are additional required TODOs in the files within the integration_tests folder and the spec.json file.
"""


# Basic full refresh stream


# Source
class SourceShipstation(AbstractSource):


    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.json
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        response = requests.get('https://ssapi.shipstation.com/users', auth=HTTPBasicAuth(config['api_key'], config['api_secret']))
        try:
            response.raise_for_status()
        except HTTPError as e:
            return False, e

        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        auth = HTTPBasicAuth(username=config["api_key"], password=config['api_secret'])
        return [Customers(authenticator=auth), Fulfillments(authenticator=auth), Products(authenticator=auth),
                Orders(authenticator=auth), Stores(authenticator=auth), Warehouses(authenticator=auth)]
