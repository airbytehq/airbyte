#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
import pkgutil
from base64 import b64encode
from typing import List, Tuple

import requests
from airbyte_protocol import AirbyteStream
from recurly import USER_AGENT
from recurly import Client as RecurlyClient
from recurly.base_errors import ApiError


class Client:
    RECURLY_BASE_URL = "https://v3.recurly.com"
    PAGINATION = 100

    def __init__(self, api_key: str):
        self.ENTITIES = ["accounts", "coupons", "invoices", "plans", "measured_units", "subscriptions", "transactions", "export_dates"]
        self._client = RecurlyClient(api_key)

        # The Authorization header is a string containing a Base-64 encoded API Key.
        self._headers = {
            "User-Agent": USER_AGENT,
            "Authorization": "Basic %s" % b64encode(api_key.encode("ascii")).decode("ascii"),
            "Accept": f"application/vnd.recurly.{self._client.api_version()}",
            "Content-Type": "application/json",
        }

    def health_check(self) -> Tuple[bool, object]:
        try:
            list(self._client.list_accounts(limit=1).items())
            return True, None
        except ApiError as err:
            return False, err.args[0]

    def get_streams(self) -> List[AirbyteStream]:
        streams = []
        for schema in self.ENTITIES:
            raw_schema = json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], f"schemas/{schema}.json"))
            streams.append(AirbyteStream(name=schema, json_schema=raw_schema))
        return streams

    def get_entities(self, entity_name) -> List[dict]:
        # There is special handling for this stream, as the API returns a list of dates
        # for which export files are available for download without pagination, all at once.
        if entity_name == "export_dates":
            resp = requests.get(f"{self.RECURLY_BASE_URL}/{entity_name}", headers=self._headers)
            return [{"dates": resp.json()["dates"]}] if resp.status_code == 200 else []
        else:
            resp = requests.get(f"{self.RECURLY_BASE_URL}/{entity_name}?limit={self.PAGINATION}", headers=self._headers)
            if resp.status_code == 200:
                entity_data = resp.json()["data"]
                while resp.json()["has_more"]:
                    resp = requests.get(f"{self.RECURLY_BASE_URL}{resp.json()['next']}", headers=self._headers)
                    entity_data += resp.json()["data"]
                return entity_data
            return []
