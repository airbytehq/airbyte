# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from datetime import date
from dateutil.relativedelta import *

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream

from .google_ads import GoogleAds
from .utils import Utils


def chunk_date_range(start_date: str, conversion_window: Optional[int]) -> Iterable[Mapping[str, any]]:
    """
    Returns a list of the beginning and ending timetsamps of each month between the start date and now.
    The return value is a list of dicts {'date': str} which can be used directly with the Slack API
    """
    intervals = []

    # applying conversion windoe
    start_date = date.fromisoformat(
        start_date) - relativedelta(days=conversion_window)
    yesterday = date.today() - relativedelta(days=1)

    # Each stream_slice contains the beginning and ending timestamp for a 24 hour period
    while start_date < yesterday:
        start = start_date
        intervals.append({"date": start.isoformat()})
        start_date = min(yesterday, start_date + relativedelta(months=1))

    return intervals


class GoogleAdsStream(Stream, ABC):
    def __init__(self, config):
        self.config = config
        self.google_ads_client = GoogleAds(**config)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return response.next_page_token

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for result in response:
            record = GoogleAds.parse_single_result(
                self.get_json_schema(), result)
            yield record

    def read_records(
        self,
        sync_mode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        if sync_mode == SyncMode.incremental:
            start_date, end_date = Utils.get_date_params_incremental(
                stream_slice, self.cursor_field)
        else:
            start_date, end_date = Utils.get_date_params_fullrefresh(
                self.config.get("start_date"))
        query = GoogleAds.convert_schema_into_query(
            self.get_json_schema(), self.name, start_date, end_date)

        pagination_complete = False
        next_page_token = None
        while not pagination_complete:
            response = self.google_ads_client.send_request(
                query, next_page_token)
            yield from self.parse_response(response, stream_state=stream_state, stream_slice=stream_slice)

            next_page_token = self.next_page_token(response)
            if not next_page_token:
                pagination_complete = True

        # Always return an empty generator just in case no records were ever yielded
        yield from []


class IncrementalGoogleAdsStream(GoogleAdsStream, ABC):
    state_checkpoint_interval = None
    CONVERSION_WINDOW_DAYS = 14

    # Just to have to default value to check with latest_Record
    TOO_OLD_DATE = "2000-01-01"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        stream_state = stream_state or {}
        start_date = stream_state.get(
            self.cursor_field) or self.config.get("start_date")
        return chunk_date_range(start_date, self.CONVERSION_WINDOW_DAYS)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}
        current_stream_state[self.cursor_field] = max(
            latest_record[self.cursor_field], current_stream_state.get(
                self.cursor_field, self.TOO_OLD_DATE))
        return current_stream_state


class AdGroupAdReport(IncrementalGoogleAdsStream):
    cursor_field = "date"
    primary_key = None


# Source
class SourceGoogleAds(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            logger.info(f"Checking the config")
            GoogleAds(**config)
            return True, None
        except Exception as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [AdGroupAdReport(config)]
