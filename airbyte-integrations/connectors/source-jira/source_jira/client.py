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

import operator
from functools import partial, reduce
from json.decoder import JSONDecodeError
from typing import Dict, Mapping, Tuple

import requests
from base_python import BaseClient
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError


class Client(BaseClient):
    """
    Jira API Reference: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
    """

    API_VERSION = 3

    ENTITIES_MAP = {
        "projects": {"url": "/project/search", "func": lambda v: v["values"], "params": {}},
        "issues": {"url": "/search", "func": lambda v: v["issues"], "params": {}},
        "issue_comments": {
            "url": "/search",
            "func": lambda v: reduce(operator.iadd, [obj["fields"]["comment"]["comments"] for obj in v["issues"]], []),
            "params": {**{"fields": ["comment"]}},
        },
        "users": {"url": "/users/search", "func": lambda v: v, "params": {}},
        "resolutions": {"url": "/resolution", "func": lambda v: v, "params": {}},
    }

    def __init__(self, api_token, domain, email):
        self.auth = HTTPBasicAuth(email, api_token)
        self.base_api_url = f"https://{domain}/rest/api/{self.API_VERSION}"
        super().__init__()

    @staticmethod
    def get_next_page(response: requests.Response, url: str, params: Dict):
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

    def lists(self, name, url, params, func, **kwargs):
        next_page = None
        request_params = params
        while True:
            if next_page:
                response = requests.get(next_page, params=request_params, auth=self.auth)
            else:
                response = requests.get(f"{self.base_api_url}{url}", params=request_params, auth=self.auth)
            data = func(response.json())
            yield from data
            next_page, request_params = self.get_next_page(response, f"{self.base_api_url}{url}", params)
            if not next_page:
                break

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {entity: partial(self.lists, name=entity, **value) for entity, value in self.ENTITIES_MAP.items()}

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            next(self.lists(name="resolutions", **self.ENTITIES_MAP["resolutions"]))

        except ConnectionError as error:
            alive, error_msg = False, str(error)
        # If the input domain is incorrect or doesn't exist, then the response would be empty, resulting in a JSONDecodeError
        except JSONDecodeError:
            alive, error_msg = (
                False,
                "Unable to connect to the Jira API with the provided credentials. Please make sure the input credentials and environment are correct.",
            )

        return alive, error_msg
