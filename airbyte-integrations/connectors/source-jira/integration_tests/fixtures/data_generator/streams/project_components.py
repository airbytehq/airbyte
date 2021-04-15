import json
import random

from .projects import ProjectRelatedMixin
from ..base import BaseStream


class ProjectComponents(BaseStream, ProjectRelatedMixin):
    list_endpoint = "component"
    generate_endpoint = "component"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_project_categories(self, url):
        for project in self.get_projects():
            for index in range(random.randrange(6)):
                payload = json.dumps({
                    "isAssigneeTypeValid": False,
                    "name": f"Component {index}",
                    "description": "This is a Jira component",
                    "project": project.get("key"),
                    "assigneeType": "PROJECT_LEAD",
                    "leadAccountId": "5fc9e78d2730d800760becc4"
                })
                response = self.make_request("POST", url, data=payload)
                print(response, response.text)

    def generate(self):
        url = self.get_url(self.generate_endpoint)
        self.generate_project_categories(url)
