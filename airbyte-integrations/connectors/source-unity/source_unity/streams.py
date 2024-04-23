#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class UnityStream(HttpStream, ABC):
    url_base = "https://services.api.unity.com/advertise/v1/organizations/%organisation_id%/apps/"
    use_cache = True  # it is used in all streams
    is_paginated = False

    def __init__(self, authenticator, config, **kwargs):
        self.config = config
        self.url_base = self.url_base.replace("%organisation_id%", self.config["organisation_id"])
        self.offset = None
        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        total = response.json().get("total")
        offset = response.json().get("offset")
        limit = response.json().get("limit")

        if offset is None or total < limit:
            return None
        else:
            self.offset += limit
            return {
                "offset": self.offset
            }

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        if response.text == "":
            return '{}'
        yield from response.json()["results"]

    def request_params(
            self,
            stream_state: Optional[Mapping[str, Any]],
            stream_slice: Optional[Mapping[str, Any]] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        if self.is_paginated:
            return {
                "offset": self.offset,
            }
        else:
            return {}

class Campaigns(UnityStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.config['campaign_set_id']}/campaigns"


class Apps(UnityStream):
    primary_key = "id"
    is_paginated = True

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""


class Creatives(UnityStream):
    primary_key = "id"
    is_paginated = True

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.config['campaign_set_id']}/creatives"


class CreativePacks(UnityStream):
    primary_key = "id"
    is_paginated = True

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"{self.config['campaign_set_id']}/creative-packs"
