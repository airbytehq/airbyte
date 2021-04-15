import json
import pathlib
import random

from ..base import BaseStream
from .issues import IssueRelatedMixin


class IssueVotes(BaseStream, IssueRelatedMixin):
    list_endpoint = "votes"
    generate_endpoint = "issue/{key}/votes"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_issue_votes(self, url):
        response = self.make_request("POST", url)
        print(response, response.text)

    def generate(self):
        issues_batch = self.get_issues()
        for item in issues_batch:
            key = item.get("key")
            url = self.get_url(self.generate_endpoint.format(key=key))
            self.generate_issue_votes(url)
