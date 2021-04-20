"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

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
        url = f"{base_url}{endpoint}"
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
