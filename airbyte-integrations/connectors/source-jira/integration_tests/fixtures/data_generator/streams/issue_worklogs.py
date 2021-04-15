import json
import pathlib
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
            payload = json.dumps({
                "timeSpentSeconds": random.randrange(600, 12000),
                "comment": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "text": f"I did some work here. {index}",
                                    "type": "text"
                                }
                            ]
                        }
                    ]
                },
                "started": "2021-04-15T01:48:52.747+0000"
            })
            response = self.make_request("POST", url, data=payload)

    def generate(self):
        issues_batch = self.get_issues()
        for item in issues_batch:
            key = item.get("key")
            url = self.get_url(self.generate_endpoint.format(key=key))
            self.generate_issue_votes(url)
