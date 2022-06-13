#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping

import requests

from .base import MixpanelStream


class Cohorts(MixpanelStream):
    """Returns all of the cohorts in a given project.
    API Docs: https://developer.mixpanel.com/reference/cohorts
    Endpoint: https://mixpanel.com/api/2.0/cohorts/list

    [{
        "count": 150
        "is_visible": 1
        "description": "This cohort is visible, has an id = 1000, and currently has 150 users."
        "created": "2019-03-19 23:49:51"
        "project_id": 1
        "id": 1000
        "name": "Cohort One"
    },
    {
        "count": 25
        "is_visible": 0
        "description": "This cohort isn't visible, has an id = 2000, and currently has 25 users."
        "created": "2019-04-02 23:22:01"
        "project_id": 1
        "id": 2000
        "name": "Cohort Two"
    }
    ]

    """

    data_field: str = None
    primary_key: str = "id"

    cursor_field = "created"

    def path(self, **kwargs) -> str:
        return "cohorts/list"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        records = super().parse_response(response, stream_state=stream_state, **kwargs)
        for record in records:
            record_cursor = record.get(self.cursor_field, "")
            state_cursor = stream_state.get(self.cursor_field, "")
            if not stream_state or record_cursor >= state_cursor:
                yield record

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        state_cursor = (current_stream_state or {}).get(self.cursor_field, "")

        record_cursor = latest_record.get(self.cursor_field, self.start_date)

        return {self.cursor_field: max(state_cursor, record_cursor)}
