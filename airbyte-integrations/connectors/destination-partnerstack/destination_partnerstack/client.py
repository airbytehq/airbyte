import base64
import requests
from typing import Any, Mapping, List


class PartnerStackClient:
    def __init__(self, public_key: str, private_key: str, endpoint: str) -> None:
        self.public_key = public_key
        self.private_key = private_key
        self.endpoint = endpoint

    def _get_base_url(self) -> str:
        return f"https://api.partnerstack.com/api/v2/{self.endpoint}"

    def encode_base64(self, msg: str) -> str:
        message_bytes = msg.encode("ascii")
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode("ascii")
        return base64_message

    def _get_auth_headers(self) -> Mapping[str, Any]:
        auth_encode = self.encode_base64(f"{self.public_key}:{self.private_key}")
        return {"authorization": f"Basic {auth_encode}"}

    def write(self, request_body: List[Mapping]):
        return self._request(http_method="POST", data=request_body)

    def list(self):
        url = self._get_base_url()
        headers = headers = {"accept": "application/json", **self._get_auth_headers()}
        response = requests.request(method="GET", url=url, headers=headers)
        return response

    def _request(self, http_method: str, data: List[Mapping] = None) -> requests.Response:
        url = self._get_base_url()
        headers = {"accept": "application/json", "content-type": "application/json", **self._get_auth_headers()}
        response = requests.request(method=http_method, url=url, headers=headers, json=data)
        return response
