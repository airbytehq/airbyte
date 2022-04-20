from abc import ABC
from typing import Any, Iterable, MutableMapping, Mapping, Optional

import requests
import arrow
from .full_refresh_streams import SnipeitStream

class Events(SnipeitStream, ABC):
    primary_key = "id"
    state_checkpoint_interval = 10

    @property
    def cursor_field(self):
        return "updated_at/datetime"

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
