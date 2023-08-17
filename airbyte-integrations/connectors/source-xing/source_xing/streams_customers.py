#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping

import requests

from .streams import XingStream

DEFAULT_COLS = ["name", "agency_name"]


class Customers(XingStream):
    parent = ""
    primary_key = "id"

    def __init__(self, authenticator, config: Mapping[str, Any], **kwargs):
        super().__init__(config=config, authenticator=authenticator, parent=self.parent)

    @property
    def use_cache(self) -> bool:
        return True

    @property
    def cache_filename(self):
        return "customers.yml"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {}
        if self.config.get("customers"):
            customers = self.config.get("customers")
            if customers.get("fields"):
                params["fields"] = ",".join(customers.get("fields"))
            else:
                params["fields"] = ",".join(DEFAULT_COLS)
            return params
        else:
            params["fields"] = ",".join(DEFAULT_COLS)
        return params

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "customers"

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        if response.json():
            for x in response.json().get("data"):
                yield x
