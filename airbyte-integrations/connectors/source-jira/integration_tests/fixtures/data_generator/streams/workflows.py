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


class Workflows(BaseStream):
    list_endpoint = "workflow"
    generate_endpoint = "workflow"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_workflows(self, url):
        for index in range(30):
            payload = json.dumps(
                {
                    "name": f"Test workflow {index}",
                    "description": "This is a workflow used for Stories and Tasks",
                    "statuses": [{"id": "1"}],
                    "transitions": [{"name": "Created", "from": [], "to": "1", "type": "initial"}],
                }
            )
            self.make_request("POST", url, data=payload)

    def generate(self):
        """https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-workflow-schemes/#api-rest-api-3-workflowscheme-post"""
        url = self.get_url(self.generate_endpoint)
        self.generate_workflows(url)
