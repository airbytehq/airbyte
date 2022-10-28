from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Tuple
from copy import deepcopy

import requests
import arrow

from airbyte_cdk.sources.streams.http import HttpStream

# Basic full refresh stream
class SnipeitStream(HttpStream, ABC):
    """
    This class represents a stream output by the connector.
    This is an abstract base class meant to contain all the common functionality at the API level e.g: the API base URL, pagination strategy,
    parsing responses etc..

    Each stream should extend this class (or another abstract subclass of it) to specify behavior unique to that stream.

    Typically for REST APIs each stream corresponds to a resource in the API. For example if the API
    contains the endpoints
        - GET v1/customers
        - GET v1/employees

    then you should have three classes:
    `class SnipeitStream(HttpStream, ABC)` which is the current class
    `class Customers(SnipeitStream)` contains behavior to pull data for customers using v1/customers
    `class Employees(SnipeitStream)` contains behavior to pull data for employees using v1/employees

    If some streams implement incremental sync, it is typical to create another class
    `class IncrementalSnipeitStream((SnipeitStream), ABC)` then have concrete stream implementations extend it. An example
    is provided below.

    See the reference docs for the full list of configurable options.
    """
    def __init__(self, config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.limit_per_page: int = 500
        self.total: int = 0
        self.offset: int = 0
        self.config: dict = config

        self.stop_immediately: bool = False

    @property
    def url_base(self):
        return self.config["base_url"]

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
        if self.stop_immediately:
            return None
        elif self.offset < self.total:
            self.offset += self.limit_per_page
            return {"offset": self.offset}
        else:
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Usually contains common params e.g. pagination size etc.
        """
        if next_page_token:
            return {'limit': self.limit_per_page, 'offset': next_page_token.get("offset", None)}
        else:
            return {'limit': self.limit_per_page, 'offset': self.offset}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        self.total = response.json().get("total", 0)
        yield from response.json().get("rows", [])


# NOTE: Temporary, dirty hack to account for the import differences
#       between airbyte_cdk 0.1.53 and 0.1.55
from airbyte_cdk.sources.streams import IncrementalMixin

class Events(SnipeitStream, IncrementalMixin):
    primary_key = "id"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = {}

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state[self.cursor_field] = value

    @property
    def cursor_field(self):
        return "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        # NOTE: This was originally the key function in the max() call below
        #       I moved it out here to keep mypy happy.
        def __key_function(item: Tuple) -> Any:
            return item[1]
        if current_stream_state == {}:
            self.state = latest_record[self.cursor_field]
            return {self.cursor_field: latest_record[self.cursor_field]}
        else:
            records = {}
            records[current_stream_state[self.cursor_field]] = arrow.get(current_stream_state[self.cursor_field])
            records[latest_record[self.cursor_field]] = arrow.get(latest_record[self.cursor_field])
            # NOTE: mypy complains about records.items() not having the right type for max() but it works just fine
            #       in runtime regardless.
            latest_record = max(records.items(), key=__key_function)[0]   # type: ignore[arg-type]
            self.state[self.cursor_field] = latest_record
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

        base = response.json().get("rows", [])
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
                # NOTE: There's probably a more succint way of doing this but I can't think of it right now.
                ascending_list: list = reversed(transformed)
                only_the_newest: list = [x for x in ascending_list if _newer_than_latest(latest_record_date, x)]
                yield from only_the_newest
        else:
            ascending_list = reversed(transformed)
            yield from ascending_list

class Hardware(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "hardware/"

class Companies(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "companies/"

class Locations(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "locations/"

class Accessories(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "accessories/"

class Consumables(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "consumables/"

class Components(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "components/"

class Users(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "users/"

class StatusLabels(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "statuslabels/"

class Models(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "models/"

class Licenses(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "licenses/"

class Categories(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "categories/"

class Manufacturers(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "manufacturers/"

class Maintenances(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "maintenances/"

class Departments(SnipeitStream):
    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "departments/"
