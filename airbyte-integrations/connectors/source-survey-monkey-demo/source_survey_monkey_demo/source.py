#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union
from urllib.parse import urlparse

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator, TokenAuthenticator
import datetime


# Basic full refresh stream
class SurveyMonkeyBaseStream(HttpStream, ABC):
    def __init__(self, name: str, path: str, primary_key: Union[str, List[str]], cursor_field: Optional[str], start_date: Optional[str], **kwargs: Any) -> None:
        self._name = name
        self._path = path
        self._primary_key = primary_key
        self._cursor_field = cursor_field
        self._start_date = start_date
        self._slice_range = 365
        super().__init__(**kwargs)

    _PAGE_SIZE: int = 100

    # TODO: Fill in the url base. Required.
    url_base = "https://api.surveymonkey.com"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        links = response.json().get("links", {})
        if "next" in links:
            return {"next_url": links["next"]}
        else:
            return {}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            #FIXME: need to make sure next_url includes the params
            return urlparse(next_page_token["next_url"]).query
        else:
            return {"per_page": self._PAGE_SIZE, "include": "response_count,date_created,date_modified,language,question_count,analyze_url,preview,collect_stats"}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json().get("data", [])

    @property
    def name(self) -> str:
        return self._name

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
            return self._path

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @property
    def cursor_field(self) -> Optional[str]:
        return self._cursor_field

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        state_value = max(current_stream_state.get(self.cursor_field, ""), latest_record.get(self._cursor_field, ""))
        return {self._cursor_field: state_value} 

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        start_ts = datetime.datetime.strptime(self._start_date, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        now_ts = datetime.datetime.now().timestamp()
        if start_ts >= now_ts:
            yield from []
            return
        for start, end in self.chunk_dates(start_ts, now_ts):
            yield {"created[gte]": start, "created[lte]": end}

    def chunk_dates(self, start_date_ts: int, end_date_ts: int) -> Iterable[Tuple[int, int]]:
        step = int(self._slice_range * 24 * 60 * 60)
        after_ts = start_date_ts
        while after_ts < end_date_ts:
            before_ts = min(end_date_ts, after_ts + step)
            yield after_ts, before_ts
            after_ts = before_ts + 1


# Source
class SourceSurveyMonkeyDemo(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(config["access_token"])
        start_date = config["start_date"]
        return [SurveyMonkeyBaseStream(name="surveys", path="/v3/surveys", primary_key=None, authenticator=auth, cursor_field="date_modified", start_date=start_date)]
