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


class IssueLinks(BaseStream, IssueRelatedMixin):
    list_endpoint = "issueLink"
    generate_endpoint = "issueLink"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_issue_links(self, url):
        outward_issues = {}
        issues_batch = self.get_issues()
        for item in issues_batch:
            project_key = item.get("fields").get("project").get("key")
            outward_issue = random.randrange(2)
            if outward_issue == 1:
                outward_issues[project_key] = item
            else:
                if project_key not in outward_issues:
                    outward_issues[project_key] = item
                else:
                    for index in range(1, random.randrange(2, 11)):
                        payload = json.dumps(
                            {
                                "outwardIssue": {"key": outward_issues[project_key].get("key")},
                                "comment": {
                                    "body": {
                                        "type": "doc",
                                        "version": 1,
                                        "content": [{"type": "paragraph", "content": [{"text": "Linked related issue!", "type": "text"}]}],
                                    }
                                },
                                "inwardIssue": {"key": item.get("key")},
                                "type": {"name": "Duplicate"},
                            }
                        )
                        self.make_request("POST", url, data=payload)

    def generate(self):
        """https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-links/#api-rest-api-3-issuelink-post"""
        url = self.get_url(self.generate_endpoint)
        self.generate_issue_links(url)
