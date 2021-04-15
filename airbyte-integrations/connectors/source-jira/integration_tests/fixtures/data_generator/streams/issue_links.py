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
                        payload = json.dumps({
                            "outwardIssue": {
                                "key": outward_issues[project_key].get("key")
                            },
                            "comment": {
                                "body": {
                                    "type": "doc",
                                    "version": 1,
                                    "content": [
                                        {
                                            "type": "paragraph",
                                            "content": [
                                                {
                                                    "text": "Linked related issue!",
                                                    "type": "text"
                                                }
                                            ]
                                        }
                                    ]
                                }
                            },
                            "inwardIssue": {
                                "key": item.get("key")
                            },
                            "type": {
                                "name": "Duplicate"
                            }
                        })
                        response = self.make_request("POST", url, data=payload)

    def generate(self):
        url = self.get_url(self.generate_endpoint)
        self.generate_issue_links(url)
