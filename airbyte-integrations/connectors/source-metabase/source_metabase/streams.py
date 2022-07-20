#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, Mapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class MetabaseStream(HttpStream, ABC):
    def __init__(self, instance_api_url: str, **kwargs):
        super().__init__(**kwargs)
        self.instance_api_url = instance_api_url

    primary_key = "id"
    response_entity = None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    @property
    def url_base(self) -> str:
        return self.instance_api_url

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if self.response_entity:
            result = response_json.get(self.response_entity, [])
        else:
            result = response_json
        yield from result


class Activity(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "activity"


class Cards(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "card"


class Collections(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "collection"


class Dashboards(MetabaseStream):
    def path(self, **kwargs) -> str:
        return "dashboard"


class Users(MetabaseStream):

    response_entity = "data"

    def path(self, **kwargs) -> str:
        return "user"
