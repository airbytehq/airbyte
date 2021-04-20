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
from .filters import FilterRelatedMixin


class FilterSharing(BaseStream, FilterRelatedMixin):
    list_endpoint = "permission"
    generate_endpoint = "filter/{id}/permission"

    def extract(self, response):
        pass

    def list(self):
        pass

    def generate_filter_sharing(self, url):
        for index in range(random.randrange(4)):
            group_name = random.choice(["Test group 0", "Test group 1", "Test group 2"])
            payload = json.dumps({"type": "group", "groupname": group_name})
            self.make_request("POST", url, data=payload)

    def generate(self):
        """https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-filter-sharing/#api-rest-api-3-filter-id-permission-post"""
        filters_batch = self.get_filters()
        for item in filters_batch:
            key = item.get("id")
            url = self.get_url(self.generate_endpoint.format(id=key))
            self.generate_filter_sharing(url)
