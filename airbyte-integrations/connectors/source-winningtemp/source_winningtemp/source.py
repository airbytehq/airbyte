#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
import base64
import pendulum


# Basic full refresh stream
class WinningtempStream(HttpStream, ABC):
    url_base = "https://api.winningtemp.com"

    def __init__(self, config: Mapping[str, Any], dict_unnest=False):
        super().__init__()
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.start_date = pendulum.parse(config.get('start_date'))
        self.dict_unnest = dict_unnest

        self.access_token = None
        self.generate_access_token()

    def generate_access_token(self):
        encoded_str = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode("ascii")).decode("utf-8")
        headers = {"accept": "application/json", "Authorization": f"Basic {encoded_str}"}
        response = requests.post(f"{self.url_base}/auth", headers=headers)

        self.access_token = response.json().get("access_token", "")

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_headers(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {
            "accept": "application/json",
            "content-type": "application/*+json",
            "authorization": f"Bearer {self.access_token}"
        }

    def request_params(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def unify_response(self, response: requests.Response, **kwargs) -> List[Mapping]:
        data = response.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            if self.dict_unnest:
                unnested_data = [{**{"identifier": k}, **v} for k, v in data.items()]
                return unnested_data
            else:
                return [data]
        else:
            raise "Invalid data type of in the response"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = self.unify_response(response)
        yield from records


class WinningtempIncrementalStream(WinningtempStream, ABC):
    state_checkpoint_interval = 1

    def __init__(self, config: Mapping[str, Any], dict_unnest=False):
        super().__init__(config, dict_unnest)
        self.date_from = None
        self.date_to = None
        self.initialize_date_ragne()

    @property
    def cursor_field(self) -> str:
        return "date"

    def get_closest_prev_monday(self, date):
        return date.add(days=-((date.day_of_week - 1) % 7))

    def initialize_date_ragne(self):
        self.date_from = self.get_closest_prev_monday(self.start_date).add(days=-7)
        self.date_to = self.date_from.add(days=7)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        if self.date_from > pendulum.today():
            return None
        return {"next_date": str(self.date_from.date())}

    def request_body_data(
            self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        cursor_date = stream_state.get(self.cursor_field, self.date_from).add(days=-7)

        self.date_from = max(cursor_date, self.date_from)
        self.date_from = self.date_from.add(days=7)
        self.date_to = self.date_to.add(days=7)

        date_from_str = str(self.date_from.date())
        date_to_str = str(self.date_to.date())
        return "{" + f'"start":"{date_from_str}","end":"{date_to_str}","showIndexByGrade":true,"indexDecimals":2' + "}"

    @property
    def http_method(self) -> str:
        return "POST"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        records = self.unify_response(response)
        meta_data = {"date_from": self.date_from, "date_to": self.date_to}
        data = [{**d, **meta_data} for d in records]
        yield from data

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {self.cursor_field: self.date_from}


class SegmentationGroups(WinningtempStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "segmentation/v1/groups"


class SurveyCategories(WinningtempStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "survey/v1/Categories"


class SurveyQuestions(WinningtempStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "survey/v1/Questions"


class QueryCategory(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query/category"


class QueryAge(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query/age"


class QueryEnpsAge(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query/enps/age"


class QueryEnpsGender(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query/enps/gender"


class QueryGender(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query/gender"


class QueryGroup(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query/group"


class Query(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query"


class QueryEnps(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query/enps"


class QuerySegment(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query/segment"


class QueryEnpsSegment(WinningtempIncrementalStream):
    primary_key = "id"

    def path(
            self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "temperature/v2/query/enps/segment"


# Source
class SourceWinningtemp(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            SegmentationGroups(config=config, dict_unnest=True),
            SurveyCategories(config=config, dict_unnest=True),
            SurveyQuestions(config=config, dict_unnest=True),
            QueryCategory(config=config, dict_unnest=True),
            QueryAge(config=config, dict_unnest=True),
            QueryEnpsAge(config=config, dict_unnest=True),
            QueryEnpsGender(config=config, dict_unnest=True),
            QueryGender(config=config, dict_unnest=True),
            QueryGroup(config=config, dict_unnest=True),
            Query(config=config, dict_unnest=False),
            QueryEnps(config=config, dict_unnest=False),
            QuerySegment(config=config, dict_unnest=True),
            QueryEnpsSegment(config=config, dict_unnest=True),
        ]
