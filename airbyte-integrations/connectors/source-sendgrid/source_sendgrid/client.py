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

from airbyte_protocol import AirbyteStream, SyncMode
from python_http_client import ForbiddenError, UnauthorizedError
from sendgrid import SendGridAPIClient


class Client:
    def __init__(self, apikey: str):
        self._client = SendGridAPIClient(api_key=apikey)
        self.ENTITY_MAP = {
            "campaigns": self.campaigns,
            "lists": self.lists,
            "contacts": self.contacts,
            "stats_automations": self.stats_automations,
        }

    def health_check(self):
        try:
            self._client.client.scopes.get()
            return True, None
        except (UnauthorizedError, ForbiddenError) as err:
            return False, err.args[0]

    def get_streams(self):
        streams = []
        for schema, method in self.ENTITY_MAP.items():
            raw_schema = json.loads(pkgutil.get_data(self.__class__.__module__.split(".")[0], f"schemas/{schema}.json"))
            streams.append(AirbyteStream(name=schema, json_schema=raw_schema, supported_sync_modes=[SyncMode.full_refresh]))
        return streams

    def lists(self):
        return json.loads(self._client.client.marketing.lists.get().body)["result"]

    def campaigns(self):
        return json.loads(self._client.client.marketing.campaigns.get().body)["result"]

    def contacts(self):
        return json.loads(self._client.client.marketing.contacts.get().body)["result"]

    def stats_automations(self):
        stats_data = json.loads(self._client.client.marketing.stats.automations.get().body)["results"]
        return stats_data or []
