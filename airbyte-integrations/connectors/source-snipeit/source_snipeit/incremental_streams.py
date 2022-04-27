from abc import ABC
from typing import Any, Iterable, MutableMapping, Mapping, Tuple
from copy import deepcopy

import requests
import arrow
from .full_refresh_streams import SnipeitStream


class Events(SnipeitStream, ABC):
    primary_key = "id"
    state_checkpoint_interval = 10

    @property
    def cursor_field(self):
        return "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if current_stream_state == {}:
            return {self.cursor_field: latest_record["updated_at"]}
        else:
            records = {}
            records[current_stream_state[self.cursor_field]] = arrow.get(current_stream_state[self.cursor_field])
            records[latest_record["updated_at"]] = arrow.get(latest_record["updated_at"])
            # NOTE: This was originally the key function in the max() call below
            #       I moved it out here to keep mypy happy.
            def __key_function(item: Tuple) -> Any:
                return item[1]
            # NOTE: mypy complains about records.items() not having the right type for max() but it works just fine
            #       in runtime regardless.
            latest_record = max(records.items(), key=__key_function)[0]   # type: ignore[arg-type]
            return {self.cursor_field: latest_record}

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
        def __move_cursor_up(record: Mapping[str, Any]) -> Mapping[str, Any]:
            result: dict = deepcopy(record)
            result["updated_at"] = result["updated_at"]["datetime"]
            return result

        def _newer_than_latest(latest_record_date: arrow.Arrow, record: Mapping[str, Any]) -> bool:
            current_record_date = arrow.get(record["updated_at"])
            if current_record_date > latest_record_date:
                return True
            else:
                return False
        base = response.json().get("rows")
        self.total = response.json().get("total")
        # NOTE: Airbyte's recommendation is to transform the object so that the cursor is
        #       top-level.
        transformed = [__move_cursor_up(record) for record in base]

        if stream_state != {}:
            latest_record_date: arrow.Arrow = arrow.get(stream_state[self.cursor_field])
            if _newer_than_latest(latest_record_date, transformed[0]) == False:
                self.stop_immediately = True
                yield from []
            else:
                ascending_list = reversed(transformed)
                only_the_newest: list = [x for x in ascending_list if _newer_than_latest(latest_record_date, x)]
                yield from only_the_newest
        else:
            ascending_list = reversed(transformed)
            yield from ascending_list
