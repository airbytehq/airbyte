from abc import ABC, abstractmethod

import requests

from .auth import AuthClient


class BaseStream(ABC):
    def __init__(self):
        self.auth_client = AuthClient()
        super(BaseStream, self).__init__()

    @property
    @abstractmethod
    def list_endpoint(self):
        """List api endpoint of the stream"""

    @property
    @abstractmethod
    def generate_endpoint(self):
        """List api endpoint of the stream"""

    @abstractmethod
    def extract(self, response):
        """Extract data"""

    def get_url(self, endpoint):
        base_url = self.auth_client.get_base_url()
        url = f'{base_url}{endpoint}'
        return url

    def get_headers(self):
        headers = self.auth_client.get_headers()
        return headers

    def make_request(self, method, url, data=None, params=None, files=None):
        auth = self.auth_client.get_auth()
        headers = self.get_headers()
        response = requests.request(method, url, data=data, headers=headers, auth=auth, params=params, files=files)
        return response

    @staticmethod
    def get_next_page(response, url, params):
        next_page = None
        response_data = response.json()
        if "nextPage" in response_data:
            next_page = response_data["nextPage"]
        else:
            if all(paging_metadata in response_data for paging_metadata in ("startAt", "maxResults", "total")):
                start_at = response_data["startAt"]
                max_results = response_data["maxResults"]
                total = response_data["total"]
                end_at = start_at + max_results
                if not end_at > total:
                    next_page = url
                    params["startAt"] = end_at
                    params["maxResults"] = max_results
        return next_page, params

    def fetch_data(self, url, params):
        next_page = None
        request_params = params
        while True:
            if next_page:
                response = self.make_request("GET", next_page, params=request_params)
            else:
                response = self.make_request("GET", url, params=request_params)
            yield from self.extract(response)
            next_page, request_params = self.get_next_page(response, url, params)
            if not next_page:
                break

    @abstractmethod
    def list(self):
        """Returns list of items"""

    @abstractmethod
    def generate(self):
        """Creates batch of items"""
