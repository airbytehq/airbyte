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

from airbyte_protocol import AirbyteStream
from python_http_client import ForbiddenError, UnauthorizedError
from sendgrid import SendGridAPIClient

from .schemas import SENDGRID_SCHEMAS


class Client:
    def __init__(self, apikey: str):
        self._client = SendGridAPIClient(api_key=apikey)

    def health_check(self):
        try:
            self._client.client.scopes.get()
            return True, None
        except (UnauthorizedError, ForbiddenError) as err:
            return False, err

    def get_streams(self):
        streams = []
        for schema in SENDGRID_SCHEMAS:
            streams.append(AirbyteStream(name=schema.name, json_schema=schema.json_schema))
        return streams

    def lists(self):
        try:
            sg_lists = json.loads(self._client.client.marketing.lists.get().body)["result"]
        except ForbiddenError:
            sg_lists = []
        return sg_lists

    def campaigns(self):
        try:
            sg_campaigns = json.loads(self._client.client.marketing.campaigns.get().body)["result"]
        except ForbiddenError:
            sg_campaigns = []
        return sg_campaigns
