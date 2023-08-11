#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping, Tuple
from airbyte_cdk import AirbyteLogger

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator

from source_first_resonance_ion.config import ENDPOINTS, EndpointDetails, InputConfig
from source_first_resonance_ion.streams import PurchaseOrders, Suppliers


# Source
class SourceFirstResonanceIon(AbstractSource):
    def _getEndpoints(self, config: InputConfig) -> EndpointDetails:
        return ENDPOINTS[config["region"]][config["environment"]]

    def check_connection(self, logger: AirbyteLogger, config: InputConfig) -> Tuple[bool, Any]:
        endpoints = self._getEndpoints(config)
        auth = Oauth2Authenticator(
            client_id=config["clientId"],
            client_secret=config["clientSecret"],
            token_refresh_endpoint=endpoints["auth"] + "/auth/realms/api-keys/protocol/openid-connect/token",
            refresh_token="",
        )
        """
        TODO: Implement a connection check to validate that the user-provided config can be used to connect to the underlying API

        See https://github.com/airbytehq/airbyte/blob/master/airbyte-integrations/connectors/source-stripe/source_stripe/source.py#L232
        for an example.

        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: InputConfig) -> List[Stream]:
        """
        TODO: Replace the streams below with your own streams.

        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        # TODO remove the authenticator if not required.
        endpoints = self._getEndpoints(config)
        auth = Oauth2Authenticator(
            client_id=config["clientId"],
            client_secret=config["clientSecret"],
            grant_type="client_credentials",
            token_refresh_endpoint=endpoints["auth"] + "/auth/realms/api-keys/protocol/openid-connect/token",
            refresh_token="",
        )

        streamArgs = {"authenticator": auth, "region": config["region"], "environment": config["environment"]}
        return [PurchaseOrders(**streamArgs), Suppliers(**streamArgs)]
