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
import random

from ..base import BaseStream
from .issues import IssueRelatedMixin


class IssueWorklogs(BaseStream, IssueRelatedMixin):
    list_endpoint = "worklog"
    generate_endpoint = "issue/{key}/worklog"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_issue_votes(self, url):
        for index in range(random.randrange(1, 6)):
            payload = json.dumps(
                {
                    "timeSpentSeconds": random.randrange(600, 12000),
                    "comment": {
                        "type": "doc",
                        "version": 1,
                        "content": [{"type": "paragraph", "content": [{"text": f"I did some work here. {index}", "type": "text"}]}],
                    },
                    "started": "2021-04-15T01:48:52.747+0000",
                }
            )
            self.make_request("POST", url, data=payload)

    def generate(self):
        """https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-worklogs/#api-rest-api-3-issue-issueidorkey-worklog-id-get"""
        issues_batch = self.get_issues()
        for item in issues_batch:
            key = item.get("key")
            url = self.get_url(self.generate_endpoint.format(key=key))
            self.generate_issue_votes(url)
