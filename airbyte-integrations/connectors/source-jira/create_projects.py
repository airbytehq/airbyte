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
import pathlib

import requests
from requests.auth import HTTPBasicAuth


def create():
    source_directory = pathlib.Path(__file__).resolve().parent
    configs_path = source_directory.joinpath("secrets/config.json")
    with open(configs_path) as json_configs:
        configs = json.load(json_configs)
    auth = HTTPBasicAuth(configs.get("email"), configs.get("api_token"))
    base_api_url = f'https://{configs.get("domain")}/rest/api/3/project'

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    for index in range(1, 51):
        payload = json.dumps(
            {
                "key": f"TESTKEY{index}",
                "name": f"Test project {index}",
                "projectTypeKey": "software",
                "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-simplified-scrum-classic",
                "description": f"Test project {index} description",
                "leadAccountId": "5fc9e78d2730d800760becc4",
                "assigneeType": "PROJECT_LEAD",
            }
        )

        requests.request("POST", base_api_url, data=payload, headers=headers, auth=auth)


if __name__ == "__main__":
    create()
