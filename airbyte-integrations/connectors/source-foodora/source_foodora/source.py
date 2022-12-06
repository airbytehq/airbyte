#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


def get_vendors() -> dict:
    vendors = {
        'vendors': [
            {
                'global_entity_id': 'FO_NO',
                'vendor_id': 'n7iy',
            },
            {
                'global_entity_id': 'FO_NO',
                'vendor_id': 'u5iq',
            },
            {
                'global_entity_id': 'FO_NO',
                'vendor_id': 'zp04',
            },
            {
                'global_entity_id': 'FO_NO',
                'vendor_id': 'pv2d',
            },
        ],
    }

    return vendors

class FoodoraStream(HttpStream, ABC):
    url_base = "https://vp-bff.api.eu.prd.portal.restaurant/vendors/v1/"

    def __init__(self, config: Mapping[str, Any], **kwargs):
        super().__init__()
        self.username = config.get("username")
        self.password = config.get("password")
        self.endpoint = config.get("endpoint")

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_kwargs(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, Any] = None,
            next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        return {"verify": False}

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        token_url =f"{self.endpoint}/auth/v4/token"
        response = requests.post(token_url, json={"username": self.username, "password": self.password}, verify=False)
        return {"authorization": f"Bearer {response.json().get('accessToken')}"}

    def request_body_json(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return get_vendors()

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("vendors", [])

class OpeningHours(FoodoraStream):
    primary_key = 'vendor_id'

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "vendors"

    @property
    def http_method(self) -> str:
        return "POST"


class SourceFoodora(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        """
        :param config:  the user-input config object conforming to the connector's spec.yaml
        :param logger:  logger object
        :return Tuple[bool, any]: (True, None) if the input config can be used to connect to the API successfully, (False, error) otherwise.
        """
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        return [OpeningHours(config)]
