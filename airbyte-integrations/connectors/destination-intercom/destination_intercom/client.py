import requests

from typing import Any, Iterable, List, Mapping, Tuple, Union

class IntercomClient:
    base_url = "https://api.intercom.io/"

    supported_resources = [
        "companies",
    ]

    def __init__(self, access_token: str = None):
        self.access_token = access_token
    
    def _get_auth_headers(self) -> Mapping[str, Any]:
        return {"Authorization": f"Bearer {self.access_token}"}

    def _request(
        self,
        http_method: str,
        endpoint: str = None,
        params: Mapping[str, Any] = None,
        json: Mapping[str, Any] = None
    ) -> requests.Response:
        url = self.base_url + (endpoint or "")
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            **self._get_auth_headers()
        }

        # session = requests.Session()
        # retry = Retry(connect=3, backoff_factor=0.5)
        # adapter = HTTPAdapter(max_retries=retry)
        # session.mount("http://", adapter)
        # session.mount("https://", adapter)

        response = requests.request(method=http_method, params=params, url=url, headers=headers, json=json)
        response.raise_for_status()

        return response
