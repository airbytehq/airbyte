#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import operator
from abc import ABC
from datetime import datetime
from time import mktime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from dateutil import parser
from dateutil.tz import tzutc

DEFAULT_CURSOR = "dateCreated"


# Basic full refresh stream
class BabelforceStream(HttpStream, ABC):
    page_size = 100

    def __init__(self, region: str, **args):
        super().__init__(**args)

        self.region = region

    @property
    def url_base(self) -> str:
        return f"https://{self.region}.babelforce.com/api/v2/"

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
        pagination = response.json().get("pagination")

        if pagination.get("current"):
            return {"page": response.json().get("pagination").get("current") + 1}
        else:
            return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        :return an iterable containing each record in the response
        """
        # Babelforce calls are sorted in reverse order. To process the calls in ascending order an
        # in-memory sort is performed
        items = response.json().get("items")
        items.sort(key=operator.itemgetter("dateCreated"))
        keys = self.get_json_schema().get("properties").keys()

        for item in items:
            yield {key: val for key, val in item.items() if key in keys}


# Basic incremental stream
class IncrementalBabelforceStream(BabelforceStream, ABC):
    cursor_field = DEFAULT_CURSOR

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_updated_at = datetime(1970, 1, 1)

        if current_stream_state:
            try:
                current_updated_at = parser.parse(current_stream_state.get(self.cursor_field))
            except ValueError:
                pass

        current_updated_at = current_updated_at.replace(tzinfo=tzutc())
        latest_record_updated_at = parser.parse(latest_record.get(self.cursor_field)).replace(tzinfo=tzutc())

        return {self.cursor_field: max(latest_record_updated_at, current_updated_at).isoformat(timespec="seconds")}


class Calls(IncrementalBabelforceStream):
    primary_key = "id"

    def __init__(self, date_created_from: str = None, date_created_to: str = None, **args):
        super(Calls, self).__init__(**args)

        self.date_created_from = date_created_from
        self.date_created_to = date_created_to

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "calls/reporting"

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        page = next_page_token.get("page", 1) if next_page_token else 1

        params = {"page": page, "max": self.page_size}

        if stream_state:
            cursor_value = parser.parse(stream_state[self.cursor_field])
            self.date_created_from = int(mktime(cursor_value.timetuple()))

        if self.date_created_from:
            params.update({"filters.dateCreated.from": self.date_created_from})

        if self.date_created_to:
            params.update({"filters.dateCreated.to": self.date_created_to})

        return params


# Source
class SourceBabelforce(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = self.authenticator(access_key_id=config.get("access_key_id"), access_token=config.get("access_token"))
            calls = Calls(region=config.get("region"), authenticator=authenticator)

            test_url = f"{calls.url_base}{calls.path()}?max=1"
            response = requests.request("GET", url=test_url, headers=authenticator.get_auth_header())

            if response.ok:
                return True, None
            else:
                response.raise_for_status()
        except Exception as exception:
            return False, exception

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        date_created_from = config.get("date_created_from")
        date_created_to = config.get("date_created_to")
        region = config.get("region")

        auth = self.authenticator(access_key_id=config.get("access_key_id"), access_token=config.get("access_token"))
        return [Calls(authenticator=auth, region=region, date_created_from=date_created_from, date_created_to=date_created_to)]

    @staticmethod
    def authenticator(access_key_id: str, access_token: str) -> HttpAuthenticator:
        return BabelforceAuthenticator(access_key_id=access_key_id, access_token=access_token)


class BabelforceAuthenticator(HttpAuthenticator):
    def __init__(self, access_key_id: str, access_token: str):
        self.access_key_id = access_key_id
        self.access_token = access_token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Auth-Access-ID": self.access_key_id, "X-Auth-Access-Token": self.access_token}
