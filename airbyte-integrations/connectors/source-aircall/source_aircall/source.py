#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import BasicHttpAuthenticator

class AircallStream(HttpStream):

    # HttpStream related fields
    url_base = "https://api.aircall.io/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        return [response.json()]


class Calls(AircallStream):

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:

        return "calls"

class SourceAircall(AbstractSource):
    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            headers = {"username": config["username"], "password": config["password"]}
            resp = requests.get(f"{AircallStream.url_base}", headers=headers)
            status = resp.status_code
            logger.info(f"Ping response code: {status}")
            if status == 200:
                return True, None

        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = BasicHttpAuthenticator(username=config["username"], password=config["password"])
        return [Calls(authenticator=auth)]
