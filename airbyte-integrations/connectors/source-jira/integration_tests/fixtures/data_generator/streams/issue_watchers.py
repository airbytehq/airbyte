from ..base import BaseStream
from .issues import IssueRelatedMixin


class IssueWatchers(BaseStream, IssueRelatedMixin):
    list_endpoint = "watchers"
    generate_endpoint = "issue/{key}/watchers"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_issue_votes(self, url):
        response = self.make_request("POST", url)

    def generate(self):
        issues_batch = self.get_issues()
        for item in issues_batch:
            key = item.get("key")
            url = self.get_url(self.generate_endpoint.format(key=key))
            self.generate_issue_votes(url)
