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
import random

import requests
from requests.auth import HTTPBasicAuth


def create():
    source_directory = pathlib.Path(__file__).resolve().parent.parent.parent
    configs_path = source_directory.joinpath("secrets/config.json")
    with open(configs_path) as json_configs:
        configs = json.load(json_configs)
    auth = HTTPBasicAuth(configs.get("email"), configs.get("api_token"))
    base_api_url = f'https://{configs.get("domain")}/rest/api/3/issue'

    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    projects = ["EX", "IT", "P2", "TESTKEY1"]
    issue_types = ["10001", "10002", "10004"]

    for index in range(1, 76):
        payload = json.dumps(
            {
                "fields": {
                    "project": {"key": random.choice(projects)},
                    "issuetype": {"id": random.choice(issue_types)},
                    "summary": f"Test {index}",
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [{"type": "paragraph", "content": [{"type": "text", "text": f"Test description {index}"}]}],
                    },
                }
            }
        )

        requests.request("POST", base_api_url, data=payload, headers=headers, auth=auth)


if __name__ == "__main__":
    create()
