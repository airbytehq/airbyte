from ..base import BaseStream
from .issues import IssueRelatedMixin


class IssueAttachments(BaseStream, IssueRelatedMixin):
    list_endpoint = "attachments"
    generate_endpoint = "attachments"

    def list(self):
        pass

    def generate(self):
        issues_batch = self.get_issues()
        for item in issues_batch:
            print(item.get("key"))
