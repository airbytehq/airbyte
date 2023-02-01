#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import operator
from abc import ABC
from datetime import datetime
from time import mktime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import HttpAuthenticator
from dateutil.tz import tzutc

DEFAULT_CURSOR = "dateCreated"


class InvalidStartAndEndDateException(Exception):
    pass


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
        :param response: the most recent response from the API
        :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                If there are no more pages in the result, return None.
        """
        pagination = response.json().get("pagination")

        if pagination.get("current"):
            return {"page": pagination.get("current", 0) + 1}
        else:
            return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        Babelforce calls are sorted in reverse order. To process the calls in ascending order an in-memory sort is performed

        :return an iterable containing each record in the response
        """
        items = response.json().get("items")
        items.sort(key=operator.itemgetter("dateCreated"))
        keys = self.get_json_schema().get("properties").keys()

        for item in items:
            yield {key: val for key, val in item.items() if key in keys}


# Basic incremental stream
class IncrementalBabelforceStream(BabelforceStream, ABC):
    cursor_field = DEFAULT_CURSOR

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        if current_stream_state and current_stream_state.get(self.cursor_field):
            current_updated_at = pendulum.parse(current_stream_state.get(self.cursor_field))
        else:
            current_updated_at = datetime(1970, 1, 1)

        current_updated_at = current_updated_at.replace(tzinfo=tzutc())
        latest_record_updated_at = pendulum.parse(latest_record.get(self.cursor_field)).replace(tzinfo=tzutc())

        return {self.cursor_field: max(latest_record_updated_at, current_updated_at).isoformat(timespec="seconds")}


class Calls(IncrementalBabelforceStream):
    primary_key = "id"

    def __init__(self, date_created_from: int = None, date_created_to: int = None, **args):
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
            cursor_value = pendulum.parse(stream_state[self.cursor_field])
            self.date_created_from = int(mktime(cursor_value.timetuple()))

        if self.date_created_from and self.date_created_to and self.date_created_from > self.date_created_to:
            raise InvalidStartAndEndDateException("`date_created_from` should be less than or equal to `date_created_to`")

        if self.date_created_from:
            params.update({"filters.dateCreated.from": self.date_created_from})

        if self.date_created_to:
            params.update({"filters.dateCreated.to": self.date_created_to})

        return params


class SourceBabelforce(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            authenticator = BabelforceAuthenticator(access_key_id=config.get("access_key_id"), access_token=config.get("access_token"))
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

        auth = BabelforceAuthenticator(access_key_id=config.get("access_key_id"), access_token=config.get("access_token"))
        return [Calls(authenticator=auth, region=region, date_created_from=date_created_from, date_created_to=date_created_to)]


class BabelforceAuthenticator(HttpAuthenticator):
    def __init__(self, access_key_id: str, access_token: str):
        self.access_key_id = access_key_id
        self.access_token = access_token

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"X-Auth-Access-ID": self.access_key_id, "X-Auth-Access-Token": self.access_token}
