import pathlib
import random

from ..base import BaseStream
from .issues import IssueRelatedMixin


class IssueAttachments(BaseStream, IssueRelatedMixin):
    list_endpoint = "attachments"
    generate_endpoint = "issue/{key}/attachments"

    def get_headers(self):
        headers = {"X-Atlassian-Token": "no-check",
                   "Accept": "application/json"}
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
        with open(demo_csv_path, "rb") as demo_csv, open(demo_json_path, "rb") as demo_json, \
                open(demo_xls_path, "rb") as demo_xls, open(demo_xlsx_path, "rb") as demo_xlsx:
            files = random.sample([demo_csv, demo_json, demo_xls, demo_xlsx], random.randrange(1, 5))
            for file in files:
                files = {"file": file}
                response = self.make_request("POST", url, files=files)

    def generate(self):
        issues_batch = self.get_issues()
        for item in issues_batch:
            key = item.get("key")
            url = self.get_url(self.generate_endpoint.format(key=key))
            self.generate_issue_attempts(url)
