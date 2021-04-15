import json
import random

from ..base import BaseStream


class ProjectCategories(BaseStream):
    list_endpoint = "projectCategory"
    generate_endpoint = "projectCategory"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_project_categories(self, url):
        for index in range(10):
            payload = json.dumps({
                "name": f"Test category {index}",
                "description": f"Test Project Category {index}"
            })
            response = self.make_request("POST", url, data=payload)

    def generate(self):
        url = self.get_url(self.generate_endpoint)
        self.generate_project_categories(url)
