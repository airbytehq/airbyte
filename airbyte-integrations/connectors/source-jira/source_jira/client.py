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

import json
from functools import partial
from json.decoder import JSONDecodeError
from typing import Mapping, Tuple

import requests
from base_python import BaseClient
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError


class Client(BaseClient):
    API_VERSION = 3
    DEFAULT_ITEMS_PER_PAGE = 100

    PARAMS = {"maxResults": DEFAULT_ITEMS_PER_PAGE, "startAt": 0}
    ENTITIES_MAP = {
        "projects": {"url": "/project/search", "func": lambda v: v["values"], "params": PARAMS},
        "issues": {"url": "/search", "func": lambda v: v["issues"], "params": PARAMS},
        "issue_comments": {"url": "/search", "func": lambda v: v["issues"], "params": {**PARAMS, **{"fields": ["comment"]}}},
        "users": {"url": "/users/search", "func": lambda v: v, "params": PARAMS},
        "resolutions": None,
    }

    def __init__(self, api_token, domain, email):
        self.auth = HTTPBasicAuth(email, api_token)
        self.base_api_url = f"https://{domain}/rest/api/{self.API_VERSION}"
        super().__init__()

    def lists(self, name, **kwargs):
        while True:
            response = requests.get(f"{self.base_api_url}{kwargs['url']}", params=kwargs["params"], auth=self.auth)
            data = kwargs["func"](response.json())
            print(data)
            for d in data:
                if name == "issue_comments":
                    for comment in d["fields"]["comment"]["comments"]:
                        yield comment
                else:
                    yield d
            kwargs["params"]["startAt"] += self.DEFAULT_ITEMS_PER_PAGE
            if len(data) < self.DEFAULT_ITEMS_PER_PAGE:
                break

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {
            entity: getattr(self, f"get_{entity}", None) or partial(self.lists, name=entity, **value)
            for entity, value in self.ENTITIES_MAP.items()
        }

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            response = requests.get(f"{self.base_api_url}/users/search", params={"maxResults": 1, "startAt": 0}, auth=self.auth)

            if response.status_code == 200:
                try:
                    json.loads(response.text)
                except JSONDecodeError:
                    alive, error_msg = (
                        False,
                        "Unable to connect to the Jira API with the provided credentials. Please make sure the input credentials and environment are correct.",
                    )
            else:
                alive, error_msg = False, str(response.text)

        except ConnectionError as error:
            alive, error_msg = False, str(error)

        return alive, error_msg

    def get_resolutions(self):
        response = requests.get(f"{self.base_api_url}/resolution", auth=self.auth)

        for res in response.json():
            yield res
