import json
import random

from ..base import BaseStream
from .issues import IssueRelatedMixin


class IssueComments(BaseStream, IssueRelatedMixin):
    list_endpoint = "comment"
    generate_endpoint = "issue/{key}/comment"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_issue_comments(self, url):
        payload = json.dumps({
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque eget "
                                        "venenatis elit. Duis eu justo eget augue iaculis fermentum. Sed semper quam "
                                        "laoreet nisi egestas at posuere augue semper.",
                                "type": "text"
                            }
                        ]
                    }
                ]
            }
        })
        for index in range(random.randrange(3)):
            response = self.make_request("POST", url, data=payload)

    def generate(self):
        issues_batch = self.get_issues()
        for item in issues_batch:
            key = item.get("key")
            url = self.get_url(self.generate_endpoint.format(key=key))
            self.generate_issue_comments(url)
