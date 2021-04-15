import json
import random

from ..base import BaseStream


class IssueFields(BaseStream):
    list_endpoint = "field"
    generate_endpoint = "field"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_issue_comments(self, url):
        for index in range(1, random.randrange(2, 11)):
            payload = json.dumps({
                "searcherKey": "com.atlassian.jira.plugin.system.customfieldtypes:grouppickersearcher",
                "name": f"New custom field {index}",
                "description": "Custom field for picking groups",
                "type": "com.atlassian.jira.plugin.system.customfieldtypes:grouppicker"
            })
            response = self.make_request("POST", url, data=payload)

    def generate(self):
        url = self.get_url(self.generate_endpoint)
        self.generate_issue_comments(url)
