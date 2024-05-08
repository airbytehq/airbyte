#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Iterable, Mapping

import requests

from .base import MixpanelStream


class EngageSchema(MixpanelStream):
    """
    Engage helper stream for dynamic schema extraction.
    :: reqs_per_hour_limit: int - property is set to the value of 1 million,
       to get the sleep time close to the zero, while generating dynamic schema.
       When `reqs_per_hour_limit = 0` - it means we skip this limits.
    """

    primary_key: str = None
    data_field: str = "results"
    reqs_per_hour_limit: int = 0  # see the docstring

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
