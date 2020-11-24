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
import pkgutil

from airbyte_protocol import AirbyteStream
from mailchimp3 import MailChimp
from mailchimp3.mailchimpclient import MailChimpError

from .models import HealthCheckError


class Client:
    PAGINATION = 100

    def __init__(self, username: str, apikey: str):
        self._client = MailChimp(mc_api=apikey, mc_user=username)
        self._entities = ["Lists", "Campaigns"]

    def health_check(self):
        try:
            self._client.ping.get()
            return True, None
        except MailChimpError as err:
            return False, HealthCheckError.parse_obj(err.args[0])

    def get_streams(self):
        streams = []
        for schema in self._entities:
            raw_schema = json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], f"schemas/{schema}.json"))
            streams.append(AirbyteStream(name=schema, json_schema=raw_schema))
        return streams

    def lists(self):
        limit = self._client.lists.all(count=1)["total_items"]

        offset = 0
        while offset < limit:
            for mc_list in self._client.lists.all(count=self.PAGINATION, offset=offset)["lists"]:
                yield mc_list
            offset += self.PAGINATION

    def campaigns(self):
        limit = self._client.campaigns.all(count=1)["total_items"]

        offset = 0
        while offset < limit:
            for mc_campaigns in self._client.campaigns.all(count=self.PAGINATION, offset=offset)["campaigns"]:
                yield mc_campaigns
            offset += self.PAGINATION
