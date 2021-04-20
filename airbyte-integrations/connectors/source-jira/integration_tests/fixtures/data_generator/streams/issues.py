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

from ..base import BaseStream


class Issues(BaseStream):
    list_endpoint = "search"
    generate_endpoint = "issue"

    def extract(self, response):
        if response.status_code == 404:
            issues = []
        else:
            issues = response.json().get("issues")
        return issues

    def list(self):
        """https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-search/#api-rest-api-3-search-get"""
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
