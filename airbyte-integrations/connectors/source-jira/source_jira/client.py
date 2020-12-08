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
from json.decoder import JSONDecodeError
from typing import Mapping, Tuple

import requests
from base_python import BaseClient
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError


class Client(BaseClient):
    API_VERSION = 3
    DEFAULT_ITEMS_PER_PAGE = 1
    ENTITIES = ["projects", "issues", "issue_comments", "resolutions", "users"]

    def __init__(self, api_token, domain, email):
        self.auth = HTTPBasicAuth(email, api_token)
        self.headers = {"Accept": "application/json"}
        self.base_api_url = f"https://{domain}/rest/api/{self.API_VERSION}"
        super().__init__()

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {entity: getattr(self, f"get_{entity}") for entity in self.ENTITIES}

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            response = requests.get(
                f"{self.base_api_url}/users/search", headers=self.headers, params={"maxResults": 1, "startAt": 0}, auth=self.auth
            )

            if response.status_code == 200:
                try:
                    json.loads(response.text)
                except JSONDecodeError:
                    alive, error_msg = False, "Some text"
            else:
                alive, error_msg = False, str(response.text)

        except ConnectionError as error:
            alive, error_msg = False, str(error)

        return alive, error_msg

    def get_projects(self):
        params = {"maxResults": self.DEFAULT_ITEMS_PER_PAGE, "startAt": 0}
        while True:
            response = requests.get(
                f"{self.base_api_url}/project/search", headers=self.headers, params=params, auth=self.auth
            )
            projects = response.json()['values']
            for project in projects:
                yield project
            params["startAt"] += self.DEFAULT_ITEMS_PER_PAGE
            if len(projects) < self.DEFAULT_ITEMS_PER_PAGE:
                break
        # response = requests.get(
        #     f"{self.base_api_url}/project/search", headers=self.headers, params={"maxResults": self.DEFAULT_ITEMS_PER_PAGE, "startAt": 0}, auth=self.auth
        # )
        #
        # data = response.json()
        # for project in data['values']:
        #     yield project
        #
        # while not data['isLast']:
        #     response = requests.get(
        #         data['nextPage'], headers=self.headers, auth=self.auth
        #     )
        #
        #     data = response.json()
        #     for project in data['values']:
        #         yield project

    def get_issues(self):
        params = {"maxResults": self.DEFAULT_ITEMS_PER_PAGE, "startAt": 0}
        while True:
            response = requests.get(
                f"{self.base_api_url}/search", headers=self.headers, params=params, auth=self.auth
            )
            issues = response.json()['issues']
            for issue in issues:
                yield issue
            params["startAt"] += self.DEFAULT_ITEMS_PER_PAGE
            if len(issues) < self.DEFAULT_ITEMS_PER_PAGE:
                break

    def get_issue_comments(self):
        params = {"maxResults": self.DEFAULT_ITEMS_PER_PAGE, "startAt": 0, 'fields': ['comment']}
        while True:
            response = requests.get(
                f"{self.base_api_url}/search", headers=self.headers, params=params, auth=self.auth
            )
            issues = response.json()['issues']
            for issue in issues:
                for comment in issue['fields']['comment']['comments']:
                    yield comment
            params["startAt"] += self.DEFAULT_ITEMS_PER_PAGE
            if len(issues) < self.DEFAULT_ITEMS_PER_PAGE:
                break

    def get_resolutions(self):
        response = requests.get(
            f"{self.base_api_url}/resolution", headers=self.headers, auth=self.auth
        )

        for res in response.json():
            yield res

    def get_users(self):
        params = {"maxResults": self.DEFAULT_ITEMS_PER_PAGE, "startAt": 0}
        while True:
            response = requests.get(
                f"{self.base_api_url}/users/search", headers=self.headers, params=params, auth=self.auth
            )
            users = response.json()
            for user in users:
                yield user
            params["startAt"] += self.DEFAULT_ITEMS_PER_PAGE
            if len(users) < self.DEFAULT_ITEMS_PER_PAGE:
                break
