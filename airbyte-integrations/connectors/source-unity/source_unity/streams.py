#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Dict

import requests
import logging
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator


class UnityStream(HttpStream, ABC):
    url_base = "https://services.api.unity.com/advertise/v1/organizations/%organisation_id%/apps/"
    use_cache = True  # it is used in all streams
    is_paginated = False

    def __init__(self, authenticator, config, **kwargs):
        self.config = config
        self.url_base = self.url_base.replace("%organisation_id%", self.config["organisation_id"])
        self.offset = 0
        super().__init__(authenticator=authenticator)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if not self.is_paginated:
            return None

        if response.json().get("results") and len(response.json().get("results")) == 0:
            return None

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

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Dict[str, Any]]:
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


class Apps(UnityStream):
    primary_key = "id"
    is_paginated = True
    use_cache = True

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Dict[str, Any]]:
        records = super().parse_response(response, **kwargs)
        for record in records:
            record['organisation_id'] = self.config["organisation_id"]
            yield record

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""


class AppsSubStream(HttpSubStream, UnityStream):
    backoff = 120
    # raise_on_http_errors = False
    use_cache = False
    path_suffix = None

    def __init__(self, authenticator: TokenAuthenticator, config, **kwargs):
        self.config = config
        super().__init__(
            authenticator=authenticator,
            config=config,
            parent=Apps(authenticator=authenticator, config=config),
        )

    def parse_response(self, response: requests.Response, stream_slice: Mapping[str, Any], **kwargs) -> Iterable[Dict[str, Any]]:
        records = super().parse_response(response, stream_slice, **kwargs)
        for record in records:
            record['organisation_id'] = self.config["organisation_id"]
            record['campaign_set_id'] = stream_slice["parent"]["id"]
            yield record

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        campaign_set_id = stream_slice["parent"]["id"]
        return f"{campaign_set_id}/{self.path_suffix}"


class Campaigns(AppsSubStream):
    primary_key = "id"
    path_suffix = "campaigns"


class Creatives(AppsSubStream):
    primary_key = "id"
    is_paginated = True
    path_suffix = "creatives"


class CreativePacks(AppsSubStream):
    primary_key = "id"
    is_paginated = True
    path_suffix = "creative-packs"
