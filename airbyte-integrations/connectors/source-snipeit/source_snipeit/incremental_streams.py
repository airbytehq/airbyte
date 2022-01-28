from abc import ABC
from typing import Any, Iterable, MutableMapping, Mapping, Optional

import requests
import arrow
from .full_refresh_streams import SnipeitStream

class Events(SnipeitStream, ABC):
    primary_key = "id"
    state_checkpoint_interval = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit_per_page: int = 10000
        self.total: int = 0
        self.offset: int = 0

        # NOTE: Used to signal the connector to stop paginating so as to stop the sync
        self.stop_immediately: bool = False

    @property
    def cursor_field(self):
        return "updated_at/datetime"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method should return a Mapping (e.g: dict) containing whatever information required to make paginated requests. This dict is passed
        to most other methods in this class to help you form headers, request bodies, query params, etc..

        For example, if the API accepts a 'page' parameter to determine which page of the result to return, and a response from the API contains a
        'page' number, then this method should probably return a dict {'page': response.json()['page'] + 1} to increment the page count by 1.
        The request_params method should then read the input next_page_token and set the 'page' param to next_page_token['page'].

        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        # NOTE: This function is overridden so that I can include functionality to immediately
        #       stop the sync should the latest record not be up-to-date.
        if self.stop_immediately:
            return {}
        elif self.offset < self.total:
            self.offset += self.limit_per_page
            return {"offset": self.offset}
        else:
            return {}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if current_stream_state == {}:
            return {self.cursor_field: latest_record["updated_at"]["datetime"]}
        else:
            records = {}
            records[current_stream_state[self.cursor_field]] = arrow.get(current_stream_state[self.cursor_field])
            records[latest_record["updated_at"]["datetime"]] = arrow.get(latest_record["updated_at"]["datetime"])
            latest_record = max(records.items(), key=lambda x: x[1])
            return {self.cursor_field: latest_record[0]}

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "reports/activity/"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        TODO: Override this method to define any query parameters to be set. Remove this method if you don't need to define request params.
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            return {'limit': self.limit_per_page, 'offset': next_page_token.get("offset", None)}
        else:
            return {'limit': self.limit_per_page, 'offset': self.offset}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any] , **kwargs) -> Iterable[Mapping]:
        """
        Parses response and returns a result set suitable for incremental sync. It takes in the stream state saved
        by Airbyte, and uses it to filter out records that have already been synced, leaving only the newest records.

        :return an iterable containing each record in the response
        """
        def _newer_than_latest(latest_record_date: arrow.Arrow, record: Mapping[str, Any]) -> bool:
            current_record_date = arrow.get(record["updated_at"]["datetime"])
            if current_record_date > latest_record_date:
                return True
            else:
                return False

        base: list = response.json().get("rows")
        self.total = response.json().get("total")

        if stream_state != {}:
            latest_record_date: arrow.Arrow = arrow.get(stream_state[self.cursor_field])
            if _newer_than_latest(latest_record_date, base[0]) == False:
                self.stop_immediately = True
                yield from []
            else:
                # NOTE: There's probably a more succint way of doing this but I can't think of it right now.
                ascending_list = reversed(base)
                only_the_newest: list = [x for x in ascending_list if _newer_than_latest(latest_record_date, x)]
                yield from only_the_newest
        else:
            ascending_list = reversed(base)
            yield from ascending_list