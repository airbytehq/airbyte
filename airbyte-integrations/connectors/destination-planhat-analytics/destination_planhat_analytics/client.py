from typing import Any, Mapping, List

import requests
import json


class PlanHatClient:
    def __init__(self, tenant_uuid: str, batch_size: str, api_method: Mapping[str, Any]) -> None:
        self.tenant_uuid = tenant_uuid
        self.batch_size = batch_size
        self.endpoint = api_method.get("url")
        self.api_token = api_method.get("api_token", None)

    def write(self, request_body: List[Mapping]):
        return self._request("POST", data=request_body)

    def _get_base_url(self) -> str:
        return f"{self.endpoint}/{self.tenant_uuid}"

    def _get_auth_headers(self) -> Mapping[str, Any]:
        return {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}

    def _request(self, http_method: str, data: List[Mapping] = None) -> requests.Response:
        url = self._get_base_url()
        headers = {"Content-Type": "application/json", **self._get_auth_headers()}
        response = requests.request(method=http_method, url=url, headers=headers, json=data)
        return response
