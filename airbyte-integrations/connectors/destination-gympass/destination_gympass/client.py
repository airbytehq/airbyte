from typing import Any, Iterable, List, Mapping, Tuple, Union
import logging
import requests

logger = logging.getLogger("airbyte")


class GympassClient:
    """Client for Gympass API."""
    buffer = []
    BASE_URL = "https://api.wellness.gympass.com"
    BATCH_SIZE = 1000

    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def batch_write(self, keys_and_values: list[dict[str, Any]]):
        """Write a batch of events to Gympass API."""
        request_body = keys_and_values
        logger.info(f"Writing {len(request_body)} events to Gympass API.")
        self._request(http_method="POST", json=request_body)

    def _get_events_url(self) -> str:
        """Get the URL for the events endpoint."""
        return f"{self.BASE_URL}/events"

    def _get_auth_headers(self) -> Mapping[str, Any]:
        """Get the auth headers for the request."""
        return {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    def _request(
            self, http_method: str, params: Mapping[str, Any] = None,
            json: Mapping[str, Any] = None
    ) -> requests.Response:
        """Make a request to the Gympass API."""
        url = self._get_events_url()
        headers = {"Accept": "application/json", **self._get_auth_headers()}
        try:
            response = requests.request(method=http_method, params=params, url=url, headers=headers, json=json)
        except requests.exceptions.HTTPError as err:
            logger.exception(err)
            raise err
        if response.status_code != 200:
            logger.info(f"Gympass API Response: {response.text}")
        response.raise_for_status()
        return response
