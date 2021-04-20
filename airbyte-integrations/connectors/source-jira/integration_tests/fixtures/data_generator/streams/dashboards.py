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

from ..base import BaseStream


class Dashboards(BaseStream):
    list_endpoint = "dashboard"
    generate_endpoint = "dashboard"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_dashboards(self, url):
        """https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-dashboards/#api-rest-api-3-dashboard-post"""
        for index in range(1, 20):
            payload = json.dumps(
                {
                    "name": f"Test dashboard {index}",
                    "description": "A dashboard to help auditors identify sample of issues to check.",
                    "sharePermissions": [{"type": "loggedin"}],
                }
            )
            self.make_request("POST", url, data=payload)

    def generate(self):
        url = self.get_url(self.generate_endpoint)
        self.generate_dashboards(url)
