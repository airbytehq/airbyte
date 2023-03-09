#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Mapping
from urllib import parse

import pendulum
import requests
from destination_heap_analytics.utils import datetime_to_string

HEADERS = {"Content_Type": "application/json"}

logger = logging.getLogger("airbyte")


class HeapClient:
    api_type = ""
    api_endpoint = ""
    check_endpoint = ""

    def __init__(self, base_url: str, app_id: str, api: Mapping[str, str]):
        self.api_type = api.get("api_type")
        self.app_id = app_id
        self.api_endpoint = parse.urljoin(base_url, f"api/{self.api_type}")
        self.check_endpoint = parse.urljoin(base_url, "api/track")

    def check(self):
        """
        send a payload to the track endpoint
        """
        return self._request(
            url=self.check_endpoint,
            json={
                "identity": "admin@heap.io",
                "idempotency_key": "airbyte-preflight-check",
                "event": "Airbyte Preflight Check",
                "timestamp": datetime_to_string(pendulum.now("UTC")),
            },
        )

    def write(self, json: Mapping[str, Any]):
        return self._request(url=self.api_endpoint, json=json)

    def _request(self, url: str, json: Mapping[str, Any] = {}) -> requests.Response:
        logger.debug(json)
        response = requests.post(url=url, headers=HEADERS, json={"app_id": self.app_id, **(json or {})})
        logger.debug(response.status_code)
        response.raise_for_status()
        return response
