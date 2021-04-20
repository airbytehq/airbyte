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

import pathlib
import random

from ..base import BaseStream
from .issues import IssueRelatedMixin


class IssueAttachments(BaseStream, IssueRelatedMixin):
    list_endpoint = "attachments"
    generate_endpoint = "issue/{key}/attachments"

    def get_headers(self):
        headers = {"X-Atlassian-Token": "no-check", "Accept": "application/json"}
        return headers

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_issue_attempts(self, url):
        attachments_directory = pathlib.Path(__file__).resolve().parent.parent.joinpath("attachments")
        demo_csv_path = attachments_directory.joinpath("demo.csv")
        demo_json_path = attachments_directory.joinpath("demo.json")
        demo_xls_path = attachments_directory.joinpath("demo.xls")
        demo_xlsx_path = attachments_directory.joinpath("demo.xlsx")
        with open(demo_csv_path, "rb") as demo_csv, open(demo_json_path, "rb") as demo_json, open(demo_xls_path, "rb") as demo_xls, open(
            demo_xlsx_path, "rb"
        ) as demo_xlsx:
            files = random.sample([demo_csv, demo_json, demo_xls, demo_xlsx], random.randrange(1, 5))
            for file in files:
                files = {"file": file}
                self.make_request("POST", url, files=files)

    def generate(self):
        """https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-attachments/#api-rest-api-3-issue-issueidorkey-attachments-post"""
        issues_batch = self.get_issues()
        for item in issues_batch:
            key = item.get("key")
            url = self.get_url(self.generate_endpoint.format(key=key))
            self.generate_issue_attempts(url)
