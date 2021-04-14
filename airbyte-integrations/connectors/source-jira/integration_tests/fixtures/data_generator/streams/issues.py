from ..base import BaseStream


class Issues(BaseStream):
    list_endpoint = 'search'
    generate_endpoint = 'issue'

    def list(self):
        url = self.get_url(endpoint=self.list_endpoint)
        response = self.make_request("GET", url)
        issues = response.json().get("issues")
        for issue in issues:
            yield issue

    def generate(self):
        pass


class IssueRelatedMixin:
    def __init__(self):
        self.issues = Issues()
        super(IssueRelatedMixin, self).__init__()

    def get_issues(self):
        issues_batch = self.issues.list()
        return issues_batch


