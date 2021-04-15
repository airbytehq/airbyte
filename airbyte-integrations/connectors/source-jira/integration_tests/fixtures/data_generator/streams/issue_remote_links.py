import json
import pathlib
import random

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
        payload = json.dumps({
            "application": {
                "name": "My Acme Tracker",
                "type": "com.acme.tracker"
            },
            "globalId": "system=https://www.mycompany.com/support&id=1",
            "relationship": "causes",
            "object": {
                "summary": "Customer support issue",
                "icon": {
                    "url16x16": "https://www.mycompany.com/support/ticket.png",
                    "title": "Support Ticket"
                },
                "title": "TSTSUP-111",
                "url": "https://www.mycompany.com/support?id=1",
                "status": {
                    "icon": {
                        "url16x16": "https://www.mycompany.com/support/resolved.png",
                        "link": "https://www.mycompany.com/support?id=1&details=closed",
                        "title": "Case Closed"
                    },
                    "resolved": True
                }
            }
        })
        response = self.make_request("POST", url, data=payload)

    def generate(self):
        issues_batch = self.get_issues()
        for item in issues_batch:
            key = item.get("key")
            url = self.get_url(self.generate_endpoint.format(key=key))
            self.generate_issue_remote_links(url)
