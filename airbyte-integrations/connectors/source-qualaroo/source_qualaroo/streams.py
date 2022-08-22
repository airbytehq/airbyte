#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream


class QualarooStream(HttpStream, ABC):
    url_base = "https://api.qualaroo.com/api/v1/"

    # Define primary key as sort key for full_refresh, or very first sync for incremental_refresh
    primary_key = "id"

    # Page size
    limit = 500

    extra_params = None

    def __init__(self, start_date: pendulum.datetime, survey_ids: List[str] = [], **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date
        self._survey_ids = survey_ids
        self._offset = 0

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        resp_json = response.json()

        if len(resp_json) == 500:
            self._offset += 500
            return {"offset": self._offset}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"limit": self.limit, "start_date": self._start_date}
        if next_page_token:
            params.update(**next_page_token)
        if self.extra_params:
            params.update(self.extra_params)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_response = response.json()
        for record in json_response:
            yield record


class ChildStreamMixin:
    parent_stream_class: Optional[QualarooStream] = None

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for item in self.parent_stream_class(config=self.config).read_records(sync_mode=sync_mode):
            yield {"id": item["id"]}


class Surveys(QualarooStream):
    """Return list of all Surveys.
    API Docs: https://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API
    Endpoint: https://api.qualaroo.com/api/v1/nudges/
    """

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return "nudges"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        survey_ids = self._survey_ids
        result = super().parse_response(response=response, **kwargs)
        for record in result:
            if not survey_ids or str(record["id"]) in survey_ids:
                yield record


class Responses(ChildStreamMixin, QualarooStream):
    """Return list of all responses of a survey.
    API Docs: hhttps://help.qualaroo.com/hc/en-us/articles/201969438-The-REST-Reporting-API
    Endpoint: https://api.qualaroo.com/api/v1/nudges/<id>/responses.json
    """

    parent_stream_class = Surveys

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        survey_id = stream_slice["survey_id"]
        return f"nudges/{survey_id}/responses.json"

    def stream_slices(self, **kwargs):
        survey_stream = Surveys(start_date=self._start_date, survey_ids=self._survey_ids, authenticator=self.authenticator)
        for survey in survey_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield {"survey_id": survey["id"]}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_data = response.json()
        # de-nest the answered_questions object if exists
        for rec in response_data:
            if "answered_questions" in rec:
                rec["answered_questions"] = list(rec["answered_questions"].values())
        yield from response_data
