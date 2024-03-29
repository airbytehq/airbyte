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
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
import logging


from typing import Any, Iterator, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import requests
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.logger import AirbyteLogFormatter
from airbyte_cdk.models import AirbyteMessage, AirbyteStateMessage, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, Level, SyncMode
from airbyte_cdk.sources.concurrent_source.concurrent_source import ConcurrentSource
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
from airbyte_cdk.sources.connector_state_manager import ConnectorStateManager
from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.source import TState
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.concurrent.adapters import StreamFacade
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor, CursorField, FinalStateCursor
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.schema_helpers import InternalConfig
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from airbyte_protocol.models import FailureType
from dateutil.relativedelta import relativedelta
from pendulum.parsing.exceptions import ParserError
from requests import codes, exceptions  # type: ignore[import]
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import IsoMillisConcurrentStreamStateConverter

_DEFAULT_CONCURRENCY = 10
_MAX_CONCURRENCY = 10
_logger = logging.getLogger("airbyte")

# Basic full refresh stream
class SurveyMonkeyBaseStream(HttpStream, ABC):
    state_converter = IsoMillisConcurrentStreamStateConverter()

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
        return {self._cursor_field: datetime.datetime.strptime(state_value, "%Y-%m-%dT%H:%M:%SZ").timestamp()} 

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        start_ts = datetime.datetime.strptime(self._start_date, "%Y-%m-%dT%H:%M:%SZ").timestamp()
        now_ts = datetime.datetime.now().timestamp()
        if start_ts >= now_ts:
            yield from []
            return
        for start, end in self.chunk_dates(start_ts, now_ts):
            yield {"start_date": datetime.datetime.fromtimestamp(start).strftime("%Y-%m-%dT%H:%M:%SZ"), "end_date": datetime.datetime.fromtimestamp(end).strftime("%Y-%m-%dT%H:%M:%SZ")}

    def chunk_dates(self, start_date_ts: int, end_date_ts: int) -> Iterable[Tuple[int, int]]:
        step = int(self._slice_range * 24 * 60 * 60)
        after_ts = start_date_ts
        while after_ts < end_date_ts:
            before_ts = min(end_date_ts, after_ts + step)
            yield after_ts, before_ts
            after_ts = before_ts + 1


# Source
class SourceSurveyMonkeyDemo(ConcurrentSourceAdapter):
    message_repository = InMemoryMessageRepository(Level(AirbyteLogFormatter.level_mapping[_logger.level]))

    def __init__(self, config: Optional[Mapping[str, Any]], state: Optional[Mapping[str, Any]]):
        if config:
            concurrency_level = min(config.get("num_workers", _DEFAULT_CONCURRENCY), _MAX_CONCURRENCY)
        else:
            concurrency_level = _DEFAULT_CONCURRENCY
        _logger.info(f"Using concurrent cdk with concurrency level {concurrency_level}")
        concurrent_source = ConcurrentSource.create(
            concurrency_level, concurrency_level // 2, _logger, self._slice_logger, self.message_repository
        )
        super().__init__(concurrent_source)
        self._config = config
        self._state = state

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        return True, None

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = TokenAuthenticator(config["access_token"])
        start_date = config["start_date"]

        synchronous_streams = [
            SurveyMonkeyBaseStream(name="surveys", path="/v3/surveys", primary_key=None, authenticator=auth, cursor_field="date_modified", start_date=start_date)
        ]
        state_manager = ConnectorStateManager(stream_instance_map={s.name: s for s in synchronous_streams}, state=self._state)

        configured_streams = []

        for stream in synchronous_streams:

            if stream.cursor_field:
                cursor_field = CursorField(stream.cursor_field)
                legacy_state = state_manager.get_stream_state(stream.name, stream.namespace)
                cursor = ConcurrentCursor(
                    stream.name,
                    stream.namespace,
                    legacy_state,
                    self.message_repository,
                    state_manager,
                    stream.state_converter,
                    cursor_field,
                    self._get_slice_boundary_fields(stream, state_manager),
                    config["start_date"],
                )
            configured_streams.append (
                StreamFacade.create_from_stream(stream,
                                                self,
                                                _logger,
                                                legacy_state,
                                                cursor)
                )
        return configured_streams
    def _get_slice_boundary_fields(self, stream: Stream, state_manager: ConnectorStateManager) -> Optional[Tuple[str, str]]:
        return ("start_date", "end_date")