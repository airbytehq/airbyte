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
from python_http_client import UnauthorizedError
from sendgrid import SendGridAPIClient

from .models import HealthCheckError


class Client:
    def __init__(self, apikey: str):
        self._client = SendGridAPIClient(api_key=apikey)
        self._entities = ["Lists", "Campaigns"]

        """ TODO:
        Authorized Apps
        Automations
        Campaign Folders
        Chimp Chatter Activity
        Connected Sites
        Conversations
        E-Commerce Stores
        Facebook Ads
        Files
        Landing Pages
        Ping
        Reports
        """

    def health_check(self):
        try:
            self._client.client.marketing.lists.get()
            return True, None
        except UnauthorizedError as err:
            return False, HealthCheckError.parse_obj(err.args[0])

    def get_streams(self):
        streams = [
            {
                "name": "Lists",
                "json_schema": {
                    "type": "object",
                    "title": "Subscriber List",
                    "description": "Information about a specific list.",
                    "properties": {
                        "id": {
                            "type": "string",
                            "title": "List ID",
                            "description": "A string that uniquely identifies this list.",
                            "readOnly": True,
                        },
                        "name": {"type": "string", "title": "List Name", "description": "The name of the list."},
                        "contact_count": {
                            "type": "integer",
                            "title": "List Contact",
                            "description": "[Contact information displayed in campaign footers](https://mailchimp.com/help/about-campaign-footers/) to comply with international spam laws.",
                        },
                        "_metadata": {
                            "type": "object",
                            "title": "Statistics",
                            "description": "Stats for the list. Many of these are cached for at least five minutes.",
                            "readOnly": True,
                            "properties": {
                                "self": {
                                    "type": "string",
                                    "format": "date-time",
                                    "title": "Campaign Last Sent",
                                    "description": "The date and time the last campaign was sent to this list in ISO 8601 format. This is updated when a campaign is sent to 10 or more recipients.",
                                    "readOnly": True,
                                }
                            },
                        },
                    },
                },
            },
            {
                "name": "Campaigns",
                "json_schema": {
                    "type": "object",
                    "title": "Campaign",
                    "description": "A summary of an individual campaign's settings and content.",
                    "properties": {
                        "id": {
                            "type": "string",
                            "title": "Campaign ID",
                            "description": "A string that uniquely identifies this campaign.",
                            "readOnly": True,
                        },
                        "name": {
                            "type": "string",
                            "title": "Archive URL",
                            "description": "The link to the campaign's archive version in ISO 8601 format.",
                            "readOnly": True,
                        },
                        "create_at": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Create Time",
                            "description": "The date and time the campaign was created in ISO 8601 format.",
                            "readOnly": True,
                        },
                        "status": {"type": "string"},
                        "updated_at": {
                            "type": "string",
                            "format": "date-time",
                            "title": "Send Time",
                            "description": "The date and time a campaign was sent.",
                            "readOnly": True,
                        },
                        "is_abtest": {
                            "type": "boolean",
                            "title": "Needs Block Refresh",
                            "description": "Determines if the campaign needs its blocks refreshed by opening the web-based campaign editor. Deprecated and will always return false.",
                            "readOnly": True,
                        },
                    },
                },
            },
        ]
        strems_n = []
        for s in streams:
            strems_n.append(AirbyteStream(name=s["name"], json_schema=s["json_schema"]))
        return streams

    def lists(self):
        return json.loads(self._client.client.marketing.lists.get().body)["result"]

    def campaigns(self):
        return json.loads(self._client.client.marketing.campaigns.get().body)["result"]
