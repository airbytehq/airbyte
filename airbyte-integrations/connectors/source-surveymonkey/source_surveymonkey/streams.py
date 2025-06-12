#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import tempfile
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
import vcr

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import CheckpointMixin
from airbyte_cdk.sources.streams.http import HttpStream


cache_file = tempfile.NamedTemporaryFile()


class SurveymonkeyStream(HttpStream, ABC):
    url_base = "https://api.surveymonkey.com/v3/"
    primary_key = "id"
    data_field = "data"
    default_backoff_time: int = 60  # secs

    def __init__(self, start_date: pendulum.datetime, survey_ids: List[str], **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date
        self._survey_ids = survey_ids

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        links = resp_json.get("links", {})
        if links.get("next"):
            next_query_string = urllib.parse.urlsplit(links["next"]).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            return params

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token or {}

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        We need to cache all requests to all endpoints during iteration.
        This API is very very rate limited, we need to reuse everything possible.
        We use the "new_episodes" record mode to save and reuse all requests in slices, details, etc..
        """
        with vcr.use_cassette(cache_file.name, record_mode="new_episodes", serializer="json", decode_compressed_response=True):
            try:
                yield from super().read_records(
                    sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
                )
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    yield from []
                else:
                    raise e

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        """
        https://developer.surveymonkey.com/api/v3/#headers
        X-Ratelimit-App-Global-Minute-Remaining - Number of remaining requests app has before hitting per minute limit
        X-Ratelimit-App-Global-Minute-Reset     - Number of seconds until the rate limit remaining resets
        Limits: https://developer.surveymonkey.com/api/v3/#request-and-response-limits
        Max Requests Per Day - 500
        Max Requests Per Minute - 120
        Real limits from API response headers:
        "X-Ratelimit-App-Global-Minute-Limit": "720"
        "X-Ratelimit-App-Global-Day-Limit": "500000"
        """
        # Stop for 60 secs if less than 1 request remains before we hit minute limit
        minute_limit_remaining = response.headers.get("X-Ratelimit-App-Global-Minute-Remaining", "100")
        if int(minute_limit_remaining) <= 1:
            return self.default_backoff_time

    def raise_error_from_response(self, response_json):
        """
        this method use in all parse responses
        including those who does not inherit / super() due to
        necessity use raw response instead of accessing `data_field`
        """
        if response_json.get("error"):
            raise Exception(repr(response_json.get("error")))

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        self.raise_error_from_response(response_json=response_json)

        if self.data_field:
            yield from response_json.get(self.data_field, [])
        else:
            yield response_json


class IncrementalSurveymonkeyStream(SurveymonkeyStream, CheckpointMixin, ABC):
    state_checkpoint_interval = 1000

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._state = None

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        pass

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]):
        self._state = value

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        for record in super().read_records(sync_mode, cursor_field, stream_slice, stream_state):
            self.state = self._get_updated_state(self.state, record)
            yield record

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        current_stream_state = current_stream_state or {}
        state_value = max(current_stream_state.get(self.cursor_field, ""), latest_record.get(self.cursor_field, ""))
        return {self.cursor_field: state_value}


class SurveyIds(IncrementalSurveymonkeyStream):
    cursor_field = "date_modified"

    def path(self, **kwargs) -> str:
        return "surveys"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["sort_order"] = "ASC"
        params["sort_by"] = self.cursor_field
        params["per_page"] = 1000  # maybe as user input or bigger value
        since_value = pendulum.parse(stream_state.get(self.cursor_field)) if stream_state.get(self.cursor_field) else self._start_date

        since_value = max(since_value, self._start_date)
        params["start_modified_at"] = since_value.strftime("%Y-%m-%dT%H:%M:%S")
        return params


class SurveyIDSliceMixin:
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"surveys/{stream_slice['survey_id']}/details"

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs):
        if self._survey_ids:
            yield from [{"survey_id": id} for id in self._survey_ids]
        else:
            survey_stream = SurveyIds(start_date=self._start_date, survey_ids=self._survey_ids, authenticator=self._session.auth)
            for survey in survey_stream.read_records(sync_mode=SyncMode.full_refresh, stream_state=stream_state):
                yield {"survey_id": survey["id"]}


class Surveys(SurveyIDSliceMixin, IncrementalSurveymonkeyStream):
    """
    Docs: https://developer.surveymonkey.com/api/v3/#surveys
    A source for stream slices. It does not contain useful info itself.
    The `surveys/id/details` endpoint contains full data about pages and questions. This data is already collected and
    gathered into array [pages] and array of arrays questions, where each inner array contains data about certain page.
    Example [[q1, q2,q3], [q4,q5]] means we have 2 pages, first page contains 3 questions q1, q2, q3, second page contains other.
    If we use the "normal" query, we need to query surveys/id/pages for page enumeration,
    then we need to query each page_id in every new request for details (because `pages` doesn't contain full info
    and valid only for enumeration), then for each page need to enumerate questions and get each question_id for details
    (since `/surveys/id/pages/id/questions` without ending /id also doesnt contain full info,
    In other words, we need to have triple stream slices, (note that api is very very rate limited
    and we need details for each survey etc), and finally we get a response similar to those we can have from `/id/details`
    endpoint. Also we will need to gather info to array in case of overrequesting, but details is already gathered it for us.
    We just need to apply filtering or small data transformation against array.
    So this way is very much better in terms of API limits.
    """

    data_field = None
    cursor_field = "date_modified"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        data = super().parse_response(response=response, stream_state=stream_state, **kwargs)
        for record in data:
            record.pop("pages", None)  # remove pages data
            yield record
