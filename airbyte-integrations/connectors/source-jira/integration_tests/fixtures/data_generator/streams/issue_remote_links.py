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
from .issues import IssueRelatedMixin


class IssueRemoteLinks(BaseStream, IssueRelatedMixin):
    list_endpoint = "remotelink"
    generate_endpoint = "issue/{key}/remotelink"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_issue_remote_links(self, url):
        payload = json.dumps(
            {
                "application": {"name": "My Acme Tracker", "type": "com.acme.tracker"},
                "globalId": "system=https://www.mycompany.com/support&id=1",
                "relationship": "causes",
                "object": {
                    "summary": "Customer support issue",
                    "icon": {"url16x16": "https://www.mycompany.com/support/ticket.png", "title": "Support Ticket"},
                    "title": "TSTSUP-111",
                    "url": "https://www.mycompany.com/support?id=1",
                    "status": {
                        "icon": {
                            "url16x16": "https://www.mycompany.com/support/resolved.png",
                            "link": "https://www.mycompany.com/support?id=1&details=closed",
                            "title": "Case Closed",
                        },
                        "resolved": True,
                    },
                },
            }
        )
        self.make_request("POST", url, data=payload)

    def generate(self):
        """https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-remote-links/#api-rest-api-3-issue-issueidorkey-remotelink-post"""
        issues_batch = self.get_issues()
        for item in issues_batch:
            key = item.get("key")
            url = self.get_url(self.generate_endpoint.format(key=key))
            self.generate_issue_remote_links(url)
