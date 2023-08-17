#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Dict, Iterable, Iterator, List, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs, urlparse

import requests

from ..utils import read_full_refresh
from .base import DateSlicesMixin, IncrementalMixpanelStream, MixpanelStream


class FunnelsList(MixpanelStream):
    """List all funnels
    API Docs: https://developer.mixpanel.com/reference/funnels#funnels-list-saved
    Endpoint: https://mixpanel.com/api/2.0/funnels/list
    """

    primary_key: str = "funnel_id"
    data_field: str = None

    def path(self, **kwargs) -> str:
        return "funnels/list"


class Funnels(DateSlicesMixin, IncrementalMixpanelStream):
    """List the funnels for a given date range.
    API Docs: https://developer.mixpanel.com/reference/funnels#funnels-query
    Endpoint: https://mixpanel.com/api/2.0/funnels
    """

    primary_key: List[str] = ["funnel_id", "date"]
    data_field: str = "data"
    cursor_field: str = "date"
    min_date: str = "90"  # days
    funnels = {}

    def path(self, **kwargs) -> str:
        return "funnels"

    def get_funnel_slices(self, sync_mode) -> Iterator[dict]:
        stream = FunnelsList(**self.get_stream_params())
        return read_full_refresh(stream)  # [{'funnel_id': <funnel_id1>, 'name': <name1>}, {...}]

    def funnel_slices(self, sync_mode) -> Iterator[dict]:
        return self.get_funnel_slices(sync_mode)

    def stream_slices(
        self, sync_mode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Mapping[str, Any]]]]:
        """Return stream slices which is a combination of all funnel_ids and related date ranges, like:
        stream_slices = [
            {   'funnel_id': funnel_id1_int,
                'funnel_name': 'funnel_name1',
                'start_date': 'start_date_1'
                'end_date': 'end_date_1'
            },
            {   'funnel_id': 'funnel_id1_int',
                'funnel_name': 'funnel_name1',
                'start_date': 'start_date_2'
                'end_date': 'end_date_2'
            }
            ...
            {   'funnel_id': 'funnel_idX_int',
                'funnel_name': 'funnel_nameX',
                'start_date': 'start_date_1'
                'end_date': 'end_date_1'
            }
            ...
        ]

        # NOTE: funnel_id type:
        #    - int in funnel_slice
        #    - str in stream_state
        """
        stream_state: Dict = stream_state or {}

        # One stream slice is a combination of all funnel_slices and date_slices
        funnel_slices = self.funnel_slices(sync_mode)
        for funnel_slice in funnel_slices:
            # get single funnel state
            # save all funnels in dict(<funnel_id1>:<name1>, ...)
            self.funnels[funnel_slice["funnel_id"]] = funnel_slice["name"]
            funnel_id = str(funnel_slice["funnel_id"])
            funnel_state = stream_state.get(funnel_id)
            date_slices = super().stream_slices(sync_mode, cursor_field=cursor_field, stream_state=funnel_state)
            for date_slice in date_slices:
                yield {**funnel_slice, **date_slice}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        # NOTE: funnel_id type:
        #    - int in stream_slice
        #    - str in stream_state
        funnel_id = str(stream_slice["funnel_id"])
        funnel_state = stream_state.get(funnel_id)

        params = super().request_params(funnel_state, stream_slice, next_page_token)
        params["funnel_id"] = stream_slice["funnel_id"]
        params["unit"] = "day"
        return params

    def process_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        response.json() example:
        {
            "meta": {
                "dates": [
                    "2016-09-12"
                    "2016-09-19"
                    "2016-09-26"
                ]
            }
            "data": {
                "2016-09-12": {
                    "steps": [...]
                    "analysis": {
                        "completion": 20524
                        "starting_amount": 32688
                        "steps": 2
                        "worst": 1
                    }
                }
                "2016-09-19": {
                    ...
                }
            }
        }
        :return an iterable containing each record in the response
        """
        # extract 'funnel_id' from internal request object
        query = urlparse(response.request.path_url).query
        params = parse_qs(query)
        funnel_id = int(params["funnel_id"][0])

        # read and transform records
        records = response.json().get(self.data_field, {})
        for date_entry in records:
            # for each record add funnel_id, name
            yield {
                "funnel_id": funnel_id,
                "name": self.funnels[funnel_id],
                "date": date_entry,
                **records[date_entry],
            }

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> Mapping[str, Mapping[str, str]]:
        """Update existing stream state for particular funnel_id
        stream_state = {
            'funnel_id1_str' = {'date': 'datetime_string1'},
            'funnel_id2_str' = {'date': 'datetime_string2'},
             ...
            'funnel_idX_str' = {'date': 'datetime_stringX'},
        }
        NOTE: funnel_id1 type:
            - int in latest_record
            - str in current_stream_state
        """
        funnel_id: str = str(latest_record["funnel_id"])
        updated_state = latest_record[self.cursor_field]
        stream_state_value = current_stream_state.get(funnel_id, {}).get(self.cursor_field)
        if stream_state_value:
            updated_state = max(updated_state, stream_state_value)
        current_stream_state.setdefault(funnel_id, {})[self.cursor_field] = updated_state
        return current_stream_state
