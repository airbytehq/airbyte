#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import requests
from destination_convex.config import ConvexConfig


class ConvexClient:
    def __init__(self, config: ConvexConfig, stream_metadata: Mapping):
        self.deployment_url = config["deployment_url"]
        self.access_key = config["access_key"]
        self.stream_metadata = stream_metadata

    def batch_write(self, records: List[Mapping]):
        """
        See Convex docs: https://docs.convex.dev/http-api/#post-apiairbyte_ingress
        """
        request_body = {"streams": self.stream_metadata, "messages": records}
        return self._request("POST", endpoint="airbyte_ingress", json=request_body)

    def delete(self, keys: List[str]):
        """
        See Convex docs: https://docs.convex.dev/http-api/#put-apiclear_tables
        """
        request_body = {"tableNames": keys}
        return self._request("PUT", endpoint="clear_tables", json=request_body)

    def add_indexes(self, indexes: Mapping):
        """
        See Convex docs: https://docs.convex.dev/http-api/#put-apiadd_indexes
        """
        return self._request("PUT", "add_indexes", json={"indexes": indexes})

    def indexes_ready(self, tables: List[str]):
        """
        See Convex docs: https://docs.convex.dev/http-api/#get-apiindexes_ready
        """
        return self._request("GET", "indexes_ready", json={"tables": tables})

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
