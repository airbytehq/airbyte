#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from typing import Iterable, Mapping

import requests

from .base import DateSlicesMixin, IncrementalMixpanelStream


class Revenue(DateSlicesMixin, IncrementalMixpanelStream):
    """Get data Revenue.
    API Docs: no docs! build based on singer source
    Endpoint: https://mixpanel.com/api/2.0/engage/revenue
    """

    data_field = "results"
    primary_key = "date"
    cursor_field = "date"

    def path(self, **kwargs) -> str:
        return "engage/revenue"

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        response.json() example:
        {
            'computed_at': '2021-07-03T12:43:48.889421+00:00',
            'results': {
                '$overall': {       <-- should be skipped
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                '2021-06-01': {
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                '2021-06-02': {
                    'amount': 0.0,
                    'count': 124,
                    'paid_count': 0
                },
                ...
            },
            'session_id': '162...',
            'status': 'ok'
        }
        :return an iterable containing each record in the response
        """
        records = response.json().get(self.data_field, {})
        for date_entry in records:
            if date_entry != "$overall":
                yield {"date": date_entry, **records[date_entry]}
