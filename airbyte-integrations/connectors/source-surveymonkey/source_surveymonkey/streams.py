#
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
#

import tempfile
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
import vcr
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

cache_file = tempfile.NamedTemporaryFile()


class SurveymonkeyStream(HttpStream, ABC):
    url_base = "https://api.surveymonkey.com/v3/"
    primary_key = "id"
    data_field = "data"

    def __init__(self, start_date: pendulum.datetime, **kwargs):
        self._start_date = start_date
        super().__init__(**kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        links = resp_json.get("links", {})
        if links.get("next"):
            next_query_string = urllib.parse.urlsplit(links["next"]).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json"}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if response_json.get("error"):
            raise Exception(repr(response_json.get("error")))
        result = response_json.get(self.data_field, [])
        yield from result

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token or {}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        with vcr.use_cassette(cache_file.name, record_mode="new_episodes", serializer="json"):
            yield from super().read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )


class IncrementalSurveymonkeyStream(SurveymonkeyStream, ABC):

    state_checkpoint_interval = 1000

    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["sort_order"] = "ASC"
        params["sort_by"] = "date_modified"
        params["per_page"] = 1000  # maybe as user input or bigger value
        since_value = pendulum.parse(stream_state.get(self.cursor_field)) if stream_state.get(self.cursor_field) else self._start_date

        since_value = max(since_value, self._start_date)
        params["start_modified_at"] = since_value.strftime("%Y-%m-%dT%H:%M:%S")
        return params

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        if current_state:
            return {self.cursor_field: max(latest_state, current_state)}
        return {}


class Surveys(IncrementalSurveymonkeyStream):
    """
    Docs: https://developer.surveymonkey.com/api/v3/#surveys
    A source for stream slices. It does not contain useful info itself.
    """

    cursor_field = "date_modified"

    def path(self, **kwargs) -> str:
        return "surveys"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if response_json.get("error"):
            raise Exception(response_json.get("error"))
        result = response_json.get(self.data_field, [])
        for record in result:
            substream = SurveyDetails(survey_id=record["id"], start_date=self._start_date, authenticator=self.authenticator)
            child_record = substream.read_records(sync_mode=SyncMode.full_refresh)
            yield from child_record


class SurveyDetails(SurveymonkeyStream):
    """
    Actually stream above can just filter, sort and enumarate survey ids.
    It does not contain the needed information. I will need it as stream slice source
    in all of endpoints
    """

    def __init__(self, survey_id, start_date, **kwargs):
        self.survey_id = survey_id
        super().__init__(start_date=start_date, **kwargs)

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"surveys/{self.survey_id}/details"

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        if response_json.get("error"):
            raise Exception(response_json.get("error"))
        response_json.pop("pages", None)
        yield response_json


class SurveyPages(SurveymonkeyStream):
    """should be filled from SurveyDetails"""

    data_field = "pages"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice["survey_id"]
        return f"surveys/{survey_id}/details"

    def stream_slices(self, **kwargs):
        survey_stream = Surveys(start_date=self._start_date, authenticator=self.authenticator)
        for survey in survey_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"survey_id": survey["id"]}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        data = response_json.get(self.data_field)
        if response_json.get("error"):
            raise Exception(response_json.get("error"))
        for record in data:
            record.pop("questions", None)
            yield record


class SurveyQuestions(SurveymonkeyStream):
    """should be filled from SurveyDetails"""

    data_field = "pages"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice["survey_id"]
        return f"surveys/{survey_id}/details"

    def stream_slices(self, **kwargs):
        survey_stream = Surveys(start_date=self._start_date, authenticator=self.authenticator)
        for survey in survey_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"survey_id": survey["id"]}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        data = super().parse_response(response=response, stream_state=stream_state, **kwargs)
        for entry in data:
            page_id = entry["id"]
            questions = entry["questions"]
            for question in questions:
                question["page_id"] = page_id
                yield question


class SurveyResponses(IncrementalSurveymonkeyStream):
    """
    Docs: https://posthog.com/docs/api/events
    """

    cursor_field = "date_modified"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice["survey_id"]
        return f"surveys/{survey_id}/responses/bulk"

    def stream_slices(self, **kwargs):
        survey_stream = Surveys(start_date=self._start_date, authenticator=self.authenticator)
        for survey in survey_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"survey_id": survey["id"]}

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the campaign_id and cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        survey_id = latest_record.get("survey_id")
        latest_cursor_value = latest_record.get(self.cursor_field)
        current_stream_state = current_stream_state or {}
        current_state = current_stream_state.get(survey_id) if current_stream_state else None
        if current_state:
            current_state = current_state.get(self.cursor_field)
        current_state_value = current_state or latest_cursor_value
        max_value = max(current_state_value, latest_cursor_value)
        new_value = {self.cursor_field: max_value}

        current_stream_state[survey_id] = new_value
        return current_stream_state

    def request_params(self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)

        since_value_surv = stream_state.get(stream_slice["survey_id"])
        if since_value_surv:
            since_value = (
                pendulum.parse(since_value_surv.get(self.cursor_field)) if since_value_surv.get(self.cursor_field) else self._start_date
            )
            since_value = max(since_value, self._start_date)
        else:
            since_value = self._start_date
        params["start_modified_at"] = since_value.strftime("%Y-%m-%dT%H:%M:%S")
        return params
