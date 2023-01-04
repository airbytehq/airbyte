#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import requests
from destination_convex.config import ConvexConfig, StreamMetadata


class ConvexClient:
    def __init__(self, config: ConvexConfig):
        self.deployment_url = config["deployment_url"]
        self.access_key = config["access_key"]
        self.stream_metadata = None

    def batch_write(self, records: List[Mapping], stream_metadata: List[StreamMetadata]):
        """
        TODO: link to convex docs here
        """
        request_body = {"streams": stream_metadata, "messages": records}
        return self._request("POST", endpoint="airbyte_ingress", json=request_body)

    def delete(self, keys: List[str]):
        """
        TODO: link to convex docs here
        """
        request_body = {"tableNames": keys}
        return self._request("PUT", endpoint="clear_tables", json=request_body)

    def add_indexes(self, indexes: Mapping):
        return self._request("PUT", "add_indexes", json={"indexes": indexes})

    def get_indexes(self):
        return self._request("GET", "get_indexes")

    def _get_auth_headers(self) -> Mapping[str, Any]:
        return {"Authorization": f"Convex {self.access_key}"}

    def _request(
        self, http_method: str, endpoint: str = None, params: Mapping[str, Any] = None, json: Mapping[str, Any] = None
    ) -> requests.Response:
        url = f"{self.deployment_url}/api/{endpoint}"
        headers = {"Accept": "application/json", **self._get_auth_headers()}

        response = requests.request(method=http_method, params=params, url=url, headers=headers, json=json)

        if response.status_code != 200:
            raise Exception(response.json())
        return response
