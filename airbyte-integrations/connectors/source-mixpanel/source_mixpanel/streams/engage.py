#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Iterable, Mapping

import requests

from .base import MixpanelStream


class EngageSchema(MixpanelStream):
    """
    Engage helper stream for dynamic schema extraction.
    """

    primary_key: str = None
    data_field: str = "results"

    def path(self, **kwargs) -> str:
        return "engage/properties"

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        response.json() example:
        {
            "results": {
                "$browser": {
                    "count": 124,
                    "type": "string"
                },
                "$browser_version": {
                    "count": 124,
                    "type": "string"
                },
                ...
                "_some_custom_property": {
                    "count": 124,
                    "type": "string"
                }
            }
        }
        """
        records = response.json().get(self.data_field, {})
        for property_name in records:
            yield {
                "name": property_name,
                "type": records[property_name]["type"],
            }
