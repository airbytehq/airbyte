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

import json
import random

from ..base import BaseStream
from .projects import ProjectRelatedMixin


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
                payload = json.dumps(
                    {
                        "isAssigneeTypeValid": False,
                        "name": f"Component {index}",
                        "description": "This is a Jira component",
                        "project": project.get("key"),
                        "assigneeType": "PROJECT_LEAD",
                        "leadAccountId": "5fc9e78d2730d800760becc4",
                    }
                )
                self.make_request("POST", url, data=payload)

    def generate(self):
        """https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-project-components/#api-rest-api-3-component-post"""
        url = self.get_url(self.generate_endpoint)
        self.generate_project_categories(url)
