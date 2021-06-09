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


import math
import urllib.parse
from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import requests
from airbyte_cdk.sources.streams.http import HttpStream


class SurveymonkeyStream(HttpStream, ABC):
    url_base = "https://app.posthog.com/api/"
    primary_key = "id"
    data_field = "data"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        if resp_json.get("next"):
            next_query_string = urllib.parse.urlsplit(resp_json["next"]).query
            params = dict(urllib.parse.parse_qsl(next_query_string))
            return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Content-Type": "application/json", "User-Agent": "posthog-python/1.4.0"}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        yield from response_json.get(self.data_field, [])

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:

        params = {}
        if next_page_token:
            params.update(next_page_token)
        return params


class IncrementalSurveymonkeyStream(SurveymonkeyStream, ABC):
    """
    Because endpoints has descending order we need to save initial state value to know when to stop pagination.
    start_date is used to as a min date to filter on.
    """

    state_checkpoint_interval = 1000

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        # place for some vars if needed


    @property
    @abstractmethod
    def cursor_field(self) -> str:
        """
        Defining a cursor field indicates that a stream is incremental, so any incremental stream must extend this class
        and define a cursor field.
        """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Return next page token until we reach the page with records older than state/start_date
        """
        return super().next_page_token(response=response)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_state = latest_record.get(self.cursor_field)
        current_state = current_stream_state.get(self.cursor_field) or latest_state
        return {self.cursor_field: max(latest_state, current_state)}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        data = super().parse_response(response=response, stream_state=stream_state, **kwargs)
        for record in data:
            if record.get(self.cursor_field) >= stream_state.get(self.cursor_field, self._start_date):
                yield record

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        since_value = stream_state.get(self.cursor_field) or self._start_date
        since_value = max(since_value, self._start_date)
        params["after"] = since_value
        return params


class Surveys(IncrementalSurveymonkeyStream):
    """
    Docs: https://posthog.com/docs/api/annotations
    A source for stream slices. It does not contain useful info itself.
    """

    cursor_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "surveys"

    def request_params(self, stream_state: Mapping[str, Any], **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, **kwargs)
        params["order"] = f"-{self.cursor_field}"  # sort descending
        return params


class SurveysDetails(SurveymonkeyStream):
    """
    Actually stream above can just filter, sort and enumarate survey ids.
    It does not contain the needed information. I will need it as stream slice source
    in all of endpoints
    """
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice["survey_id"]
        return f"reports/{survey_id}"


class SurveyPages(SurveymonkeyStream):
    """
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice["survey_id"]
        return f"surveys{survey_id}/pages"

    def stream_slices(self, **kwargs):
        campaign_stream = Campaigns(authenticator=self.authenticator)
        for campaign in campaign_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": campaign["id"]}


class SurveyPagesDetails(SurveymonkeyStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice["survey_id"]
        page_id = stream_slice['page_id']
        return f"surveys{survey_id}/pages/{page_id}"


class SurveyQuestions(SurveymonkeyStream):
    """
    Docs: https://posthog.com/docs/api/events
    """

    cursor_field = "timestamp"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice["survey_id"]
        page_id = stream_slice['page_id']
        return f"surveys{survey_id}/pages/{page_id}/questions"

    def stream_slices(self, **kwargs):
        campaign_stream = Campaigns(authenticator=self.authenticator)
        for campaign in campaign_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": campaign["id"]}


class SurveyQuestionsDetails(SurveymonkeyStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice["survey_id"]
        page_id = stream_slice['page_id']
        question_id = stream_slice['question_id']
        return f"surveys{survey_id}/pages/{page_id}/questions/{question_id}"

    def stream_slices(self, **kwargs):
        campaign_stream = Campaigns(authenticator=self.authenticator)
        for campaign in campaign_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": campaign["id"]}


class SurveyResponses(IncrementalSurveymonkeyStream):
    """
    Docs: https://posthog.com/docs/api/events
    """

    data_field = "result"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice['survey_id']
        return f"surveys/{survey_id}/responses/bulk"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()
        return resp_json.get("pagination")

    def stream_slices(self, **kwargs):
        campaign_stream = Campaigns(authenticator=self.authenticator)
        for campaign in campaign_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"campaign_id": campaign["id"]}