#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Iterable

import requests

from .base import MixpanelStream


class ExportSchema(MixpanelStream):
    """
    Export helper stream for dynamic schema extraction.
    """

    primary_key: str = None
    data_field: str = None

    def path(self, **kwargs) -> str:
        return "events/properties/top"

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[str]:
        """
        response.json() example:
        {
            "$browser": {
                "count": 6
            },
            "$browser_version": {
                "count": 6
            },
            "$current_url": {
                "count": 6
            },
            "mp_lib": {
                "count": 6
            },
            "noninteraction": {
                "count": 6
            },
            "$event_name": {
                "count": 6
            },
            "$duration_s": {},
            "$event_count": {},
            "$origin_end": {},
            "$origin_start": {}
        }
        """
        records = response.json()
        for property_name in records:
            yield property_name
