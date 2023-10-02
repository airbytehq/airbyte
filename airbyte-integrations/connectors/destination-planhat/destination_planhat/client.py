from typing import Any, Mapping, List
from logging import getLogger

import requests

logger = getLogger("airbyte")


class PlanHatClient:
    def __init__(
        self,
        api_token: str,
        pobject: Mapping[str, Any],
        batch_size: int = 5000,
    ) -> None:
        self.api_token = api_token
        self.endpoint = pobject.get("endpoint")
        self.batch_size = batch_size
        self.write_buffer = []

    def _get_base_url(self) -> str:
        return f"https://api.planhat.com/{self.endpoint}"

    def _get_auth_headers(self) -> Mapping[str, Any]:
        return {"Authorization": f"Bearer {self.api_token}"}

    def _request(self, http_method: str = "PUT", data: List[Mapping] = None) -> requests.Response:
        url = self._get_base_url()
        headers = {"Content-Type": "application/json", **self._get_auth_headers()}
        response = requests.request(method=http_method, url=url, headers=headers, json=data)
        return response

    def get_list(self) -> requests.Response:
        url = self._get_base_url()
        headers = {"Content-Type": "application/json", **self._get_auth_headers()}
        return requests.request("GET", url=url, headers=headers)

    def write(self, request_body: List[Mapping]):
        return self._request("PUT", request_body)

    def queue_write_operation(self, record: Mapping):
        self.write_buffer.append(record)
        if len(self.write_buffer) == self.batch_size:
            self.flush()

    def flush(self):
        response = self.write(self.write_buffer)

        logs = response.json()
        logs_created_errors = logs['createdErrors']
        logs_updated_errors = logs['updatedErrors']

        if logs_created_errors:
            logger.warning(logs_created_errors)
        if logs_updated_errors:
            logger.warning(logs_updated_errors)

        self.write_buffer.clear()

