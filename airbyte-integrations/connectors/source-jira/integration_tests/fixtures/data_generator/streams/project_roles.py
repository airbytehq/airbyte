import json
import random

from ..base import BaseStream


class ProjectRoles(BaseStream):
    list_endpoint = "role"
    generate_endpoint = "role"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_project_roles(self, url):
        for index in range(20):
            payload = json.dumps({
                "name": f"Test role {index}",
                "description": f"Test Project Role {index}"
            })
            response = self.make_request("POST", url, data=payload)
            print(response, response.text)

    def generate(self):
        url = self.get_url(self.generate_endpoint)
        self.generate_project_roles(url)
