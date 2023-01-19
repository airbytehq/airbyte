#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, List, Mapping

import requests
from destination_convex.config import ConvexConfig


class ConvexClient:
    def __init__(self, config: ConvexConfig, stream_metadata: Mapping[str, Any]):
        self.deployment_url = config["deployment_url"]
        self.access_key = config["access_key"]
        self.stream_metadata = stream_metadata

    def batch_write(self, records: List[Mapping[str, Any]]) -> requests.Response:
        """
        See Convex docs: https://docs.convex.dev/http-api/#post-apiingressairbyte_ingress
        """
        request_body = {"streams": self.stream_metadata, "messages": records}
        return self._request("POST", endpoint="airbyte_ingress", json=request_body)

    def delete(self, keys: List[str]) -> requests.Response:
        """
        See Convex docs: https://docs.convex.dev/http-api/#put-apiingressclear_tables
        """
        request_body = {"tableNames": keys}
        return self._request("PUT", endpoint="clear_tables", json=request_body)

    def add_primary_key_indexes(self, indexes: Mapping[str, List[List[str]]]) -> requests.Response:
        """
        See Convex docs: https://docs.convex.dev/http-api/#put-apiingressadd_primary_key_indexes
        """
        return self._request("PUT", "add_primary_key_indexes", json={"indexes": indexes})

    def primary_key_indexes_ready(self, tables: List[str]) -> requests.Response:
        """
        See Convex docs: https://docs.convex.dev/http-api/#get-apiingressprimary_key_indexes_ready
        """
        return self._request("GET", "primary_key_indexes_ready", json={"tables": tables})

    def _get_auth_headers(self) -> Mapping[str, str]:
        return {"Authorization": f"Convex {self.access_key}"}

    def _request(
        self,
        http_method: str,
        endpoint: str,
        json: Mapping[str, Any],
    ) -> requests.Response:
        url = f"{self.deployment_url}/api/ingress/{endpoint}"
        headers = {
            "Accept": "application/json",
            "Convex-Client": "ingress-0.1.0",
            **self._get_auth_headers(),
        }

        response = requests.request(method=http_method, url=url, headers=headers, json=json)

        if response.status_code != 200:
            raise Exception(response.json())
        return response
