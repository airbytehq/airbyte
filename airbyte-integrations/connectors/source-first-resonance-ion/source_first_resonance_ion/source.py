#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Tuple
from airbyte_cdk import AirbyteLogger

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.models.airbyte_protocol import SyncMode
import requests

from source_first_resonance_ion.config import ENDPOINTS, EndpointDetails, InputConfig
from source_first_resonance_ion.streams import (
    CheckConnection,
    PartSubtypes,
    Parts,
    PurchaseOrderFees,
    PurchaseOrderLines,
    PurchaseOrders,
    Suppliers,
)


# Source
class SourceFirstResonanceIon(AbstractSource):
    def _getEndpoints(self, config: InputConfig) -> EndpointDetails:
        return ENDPOINTS[config["region"]][config["environment"]]

    def check_connection(self, logger: AirbyteLogger, config: InputConfig) -> Tuple[bool, Any]:
        endpoints = self._getEndpoints(config)

        try:
            auth = Oauth2Authenticator(
                client_id=config["clientId"],
                client_secret=config["clientSecret"],
                grant_type="client_credentials",
                token_refresh_endpoint=endpoints["auth"] + "/auth/realms/api-keys/protocol/openid-connect/token",
                refresh_token="",
            )
            streamArgs = {"authenticator": auth, "region": config["region"], "environment": config["environment"]}

            stream = CheckConnection(**streamArgs)
            stream.read_records(sync_mode=SyncMode.full_refresh)

            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: InputConfig) -> List[Stream]:
        endpoints = self._getEndpoints(config)
        auth = Oauth2Authenticator(
            client_id=config["clientId"],
            client_secret=config["clientSecret"],
            grant_type="client_credentials",
            token_refresh_endpoint=endpoints["auth"] + "/auth/realms/api-keys/protocol/openid-connect/token",
            refresh_token="",
        )

        streamArgs = {"authenticator": auth, "region": config["region"], "environment": config["environment"]}
        return [
            PurchaseOrders(**streamArgs),
            Suppliers(**streamArgs),
            PurchaseOrderLines(**streamArgs),
            PurchaseOrderLines(**streamArgs),
            Parts(**streamArgs),
            PartSubtypes(**streamArgs),
            PurchaseOrderFees(**streamArgs),
        ]
