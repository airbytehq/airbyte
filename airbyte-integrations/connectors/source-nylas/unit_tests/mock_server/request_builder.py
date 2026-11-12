# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http import HttpRequest


class NylasRequestBuilder:
    @staticmethod
    def grants():
        return HttpRequest(url="https://api.us.nylas.com/v3/grants", query_params={"limit": "50"})

    @staticmethod
    def calendars():
        return HttpRequest(url="https://api.us.nylas.com/v3/grants/grant-1/calendars", query_params={"limit": "50"})

    @staticmethod
    def events(calendar_id):
        return HttpRequest(
            url="https://api.us.nylas.com/v3/grants/grant-1/events",
            query_params={"calendar_id": calendar_id, "limit": "50", "start": "1788220800", "end": "1788393600"},
        )
