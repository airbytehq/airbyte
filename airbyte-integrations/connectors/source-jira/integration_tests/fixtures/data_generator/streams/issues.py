from ..base import BaseStream


class Issues(BaseStream):
    list_endpoint = 'search'
    generate_endpoint = 'issue'

    def extract(self, response):
        if response.status_code == 404:
            issues = []
        else:
            issues = response.json().get("issues")
        return issues

    def list(self):
        params = {}
        url = self.get_url(endpoint=self.list_endpoint)
        for issue in self.fetch_data(url, params):
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


