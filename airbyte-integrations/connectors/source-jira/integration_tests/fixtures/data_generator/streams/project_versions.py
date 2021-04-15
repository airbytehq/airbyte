import json
import random

from .projects import ProjectRelatedMixin
from ..base import BaseStream


class ProjectVersions(BaseStream, ProjectRelatedMixin):
    list_endpoint = "version"
    generate_endpoint = "version"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_project_versions(self, url):
        for project in self.get_projects():
            for index in range(random.randrange(6)):
                payload = json.dumps({
                    "archived": False,
                    "releaseDate": "2010-07-06",
                    "name": f"New Version {index}",
                    "description": "An excellent version",
                    "projectId": project.get("id"),
                    "released": True
                })
                response = self.make_request("POST", url, data=payload)
                print(response, response.text)

    def generate(self):
        url = self.get_url(self.generate_endpoint)
        self.generate_project_versions(url)
