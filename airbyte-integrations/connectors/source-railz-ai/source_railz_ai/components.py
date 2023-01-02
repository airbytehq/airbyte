#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import time
from dataclasses import InitVar, dataclass
from datetime import datetime
from typing import Any, Iterable, List, Mapping, Optional, Union

import requests
from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.auth.token import AbstractHeaderAuthenticator
from airbyte_cdk.sources.declarative.datetime.min_max_datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOption
from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever
from airbyte_cdk.sources.declarative.stream_slicers import DatetimeStreamSlicer, SingleSlice
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream, StreamData
from airbyte_cdk.sources.streams.http.requests_native_auth import BasicHttpAuthenticator, TokenAuthenticator
from dataclasses_jsonschema import JsonSchemaMixin
from requests.adapters import HTTPAdapter, Retry


@dataclass
class AccessTokenAuthenticator(AbstractHeaderAuthenticator, JsonSchemaMixin):
    """
    https://docs.railz.ai/reference/authentication
    """

    options: InitVar[Mapping[str, Any]]
    config: Config
    client_id: Union[InterpolatedString, str]
    secret_key: Union[InterpolatedString, str]

    def __post_init__(self, options: Mapping[str, Any]):
        self._options = options
        self.client_id = InterpolatedString.create(self.client_id, options=options)
        self.secret_key = InterpolatedString.create(self.secret_key, options=options)
        self._basic_auth = BasicHttpAuthenticator(username=self.client_id.eval(self.config), password=self.secret_key.eval(self.config))
        self._timestamp = time.time()
        self._token_auth = None
        self.url = "https://auth.railz.ai/getAccess"
        self.refresh_after = 60  # minutes

    def __call__(self, request):
        request.headers.update(self.get_auth_header())
        return request

    def check_token(self):
        if not self._token_auth or time.time() - self._timestamp > self.refresh_after * 60:
            headers = {"accept": "application/json", **self._basic_auth.get_auth_header()}
            session = requests.Session()
            retries = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
            session.mount("https://", HTTPAdapter(max_retries=retries))
            response = session.get(self.url, headers=headers)
            response.raise_for_status()
            response_json = response.json()
            self._token_auth = TokenAuthenticator(token=response_json["access_token"])
            self._timestamp = time.time()

    @property
    def auth_header(self) -> str:
        self.check_token()
        return self._token_auth._auth_header

    @property
    def token(self) -> str:
        self.check_token()
        return self._token_auth.token


@dataclass
class RailzAiParentStreamConfig(JsonSchemaMixin):
    options: InitVar[Mapping[str, Any]]
    stream: Stream

    def __post_init__(self, options: Mapping[str, Any]):
        self._options = options


@dataclass
class RailzAiServiceSlicer(SingleSlice):
    config: Config
    parent_stream_config: RailzAiParentStreamConfig
    service_names: Union[List[str], str]

    def __post_init__(self, options: Mapping[str, Any]):
        self._options = options
        self._cursor = {}
        if isinstance(self.service_names, str):
            self.service_names = InterpolatedString.create(self.service_names, options=options).eval(self.config)

    def get_stream_state(self) -> StreamState:
        return self._cursor if self._cursor else {}

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        if last_record is None:
            self._cursor.update(stream_slice)
            return

        if stream_slice["businessName"] not in self._cursor:
            self._cursor[stream_slice["businessName"]] = set()
        self._cursor[stream_slice["businessName"]].add(stream_slice["serviceName"])

    def _check_valid_service(self, connection):
        return connection["serviceName"] in self.service_names and connection["status"] in ["active", "disconnected", "expired"]

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[StreamSlice]:
        if not self.parent_stream_config:
            yield from []
        else:
            parent_stream = self.parent_stream_config.stream
            for parent_stream_slice in parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=None, stream_state=stream_state):
                empty_parent_slice = True

                for parent_record in parent_stream.read_records(
                    sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=parent_stream_slice, stream_state=None
                ):
                    # Skip non-records (eg AirbyteLogMessage)
                    if isinstance(parent_record, AirbyteMessage):
                        if parent_record.type == Type.RECORD:
                            parent_record = parent_record.record.data
                        else:
                            continue

                    for connection in parent_record["connections"]:
                        if self._check_valid_service(connection):
                            empty_parent_slice = False
                            yield {"businessName": parent_record["businessName"], "serviceName": connection["serviceName"]}

                if empty_parent_slice:
                    yield from []

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        options = {}
        if stream_slice:
            options = {
                "businessName": stream_slice["businessName"],
                "serviceName": stream_slice["serviceName"],
            }
        return options


@dataclass
class RailzAiIncrementalSlicer(DatetimeStreamSlicer):
    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        options = {}
        if stream_slice:
            start_date = (stream_slice.get(self.stream_slice_field_start.eval(self.config)),)
            end_date = (stream_slice.get(self.stream_slice_field_end.eval(self.config)),)
            if isinstance(start_date, tuple):
                start_date = start_date[0]
            if isinstance(end_date, tuple):
                end_date = end_date[0]
            options = {self.cursor_field.eval(self.config): f"gte:{start_date};lte:{end_date}"}
        return options


@dataclass
class RailzAiIncrementalReportsSlicer(DatetimeStreamSlicer):
    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        stream_slice_value_end = stream_slice.get(self.stream_slice_field_end.eval(self.config))
        last_record_value = last_record.get(self.cursor_field.eval(self.config)) if last_record else None
        if self._cursor and last_record_value:
            self._cursor = max(last_record_value, self._cursor)
        elif last_record_value:
            self._cursor = last_record_value
        if self.stream_slice_field_end:
            self._cursor_end = stream_slice_value_end


@dataclass
class RailzAiIncrementalServiceSlicer(RailzAiServiceSlicer):
    base_datetime_stream_slicer_options: Mapping[str, Any]
    _cursor_format = "%Y-%m-%dT%H:%M:%S.%f%z"

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        if last_record is None:
            self._cursor.update(stream_slice)
            return

        if stream_slice["businessName"] not in self._cursor:
            self._cursor[stream_slice["businessName"]] = {}
        if stream_slice["serviceName"] not in self._cursor[stream_slice["businessName"]]:
            self._cursor[stream_slice["businessName"]][stream_slice["serviceName"]] = {}
        service = self._cursor[stream_slice["businessName"]][stream_slice["serviceName"]]

        last_record_cursor_value = self._get_record_cursor_value(last_record)

        if self._datetime_state_start_field not in service or service[self._datetime_state_start_field] < last_record_cursor_value:
            service[self._datetime_state_start_field] = last_record_cursor_value

    def _get_record_cursor_value(self, record):
        value_unformatted = record[self._datetime_cursor_field]
        return datetime.strptime(value_unformatted, self._cursor_format).strftime("%Y-%m-%d")

    def stream_slices(self, sync_mode: SyncMode, stream_state: StreamState) -> Iterable[StreamSlice]:
        for stream_slice in super().stream_slices(sync_mode, stream_state):
            if stream_slice["businessName"] in stream_state and stream_slice["serviceName"] in stream_state[stream_slice["businessName"]]:
                datetime_stream_slicer = self._create_datetime_stream_slicer(
                    {
                        **self.base_datetime_stream_slicer_options,
                        "start_datetime": {
                            **self.base_datetime_stream_slicer_options["start_datetime"],
                            "datetime": stream_state[stream_slice["businessName"]][stream_slice["serviceName"]][
                                self._datetime_state_start_field
                            ],
                        },
                    }
                )
            else:
                datetime_stream_slicer = self._create_datetime_stream_slicer(self.base_datetime_stream_slicer_options)
            for datetime_stream_slice in datetime_stream_slicer.stream_slices(sync_mode, stream_state):
                yield {**stream_slice, **datetime_stream_slice}

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        options = {}
        if stream_slice:
            start_date = (stream_slice[self._datetime_state_start_field],)
            end_date = (stream_slice[self._datetime_state_end_field],)
            if isinstance(start_date, tuple):
                start_date = start_date[0]
            if isinstance(end_date, tuple):
                end_date = end_date[0]

            options = {
                "businessName": stream_slice["businessName"],
                "serviceName": stream_slice["serviceName"],
                self._datetime_cursor_field: f"gte:{start_date};lte:{end_date}",
            }
        return options

    @property
    def _datetime_cursor_field(self):
        datetime_stream_slicer = self._create_datetime_stream_slicer(self.base_datetime_stream_slicer_options)
        return datetime_stream_slicer.cursor_field.eval(self.config)

    @property
    def _datetime_state_start_field(self):
        datetime_stream_slicer = self._create_datetime_stream_slicer(self.base_datetime_stream_slicer_options)
        return datetime_stream_slicer.stream_slice_field_start.eval(self.config)

    @property
    def _datetime_state_end_field(self):
        datetime_stream_slicer = self._create_datetime_stream_slicer(self.base_datetime_stream_slicer_options)
        return datetime_stream_slicer.stream_slice_field_end.eval(self.config)

    @property
    def _datetime_options_start_field(self):
        datetime_stream_slicer = self._create_datetime_stream_slicer(self.base_datetime_stream_slicer_options)
        return datetime_stream_slicer.start_time_option.field_name

    @property
    def _datetime_options_end_field(self):
        datetime_stream_slicer = self._create_datetime_stream_slicer(self.base_datetime_stream_slicer_options)
        return datetime_stream_slicer.end_time_option.field_name

    def _create_datetime_stream_slicer(self, options):
        args = {
            **options,
            "start_datetime": MinMaxDatetime(**options["start_datetime"], options=self._options),
            "end_datetime": MinMaxDatetime(**options["end_datetime"], options=self._options),
            "start_time_option": RequestOption(**options["start_time_option"], options=self._options),
            "end_time_option": RequestOption(**options["end_time_option"], options=self._options),
            "options": self._options,
            "config": self.config,
        }
        return DatetimeStreamSlicer(**args)


@dataclass
class RailzAiIncrementalServiceReportsSlicer(RailzAiIncrementalServiceSlicer):
    _cursor_format = "%Y-%m-%dT%H:%M:%S%z"

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        options = {}
        if stream_slice:
            start_date = (stream_slice[self._datetime_state_start_field],)
            end_date = (stream_slice[self._datetime_state_end_field],)
            if isinstance(start_date, tuple):
                start_date = start_date[0]
            if isinstance(end_date, tuple):
                end_date = end_date[0]

            options = {
                "businessName": stream_slice["businessName"],
                "serviceName": stream_slice["serviceName"],
                self._datetime_options_start_field: start_date,
                self._datetime_options_end_field: end_date,
            }
        return options


@dataclass
class RailzAiReportsRetriever(SimpleRetriever):
    meta_fields: Union[List[str], str, None] = None
    _default_meta_fields = ("reportId",)

    def __post_init__(self, options: Mapping[str, Any]):
        super().__post_init__(options)

        if isinstance(self.meta_fields, str):
            self.meta_fields = InterpolatedString(self.meta_fields, default=None, options=options).eval(self.config)
            if not isinstance(self.meta_fields, List):
                self.meta_fields = None

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[StreamSlice] = None,
        stream_state: Optional[StreamState] = None,
    ) -> Iterable[StreamData]:
        stream_slice = stream_slice or {}

        self.paginator.reset()
        records_generator = self._read_pages(
            self.parse_records_and_emit_request_and_responses,
            stream_slice,
            stream_state,
        )

        def update_cursor_and_get_parsed_records(_record) -> Union[Iterable[Record], None]:
            if isinstance(_record, Mapping):
                meta_fields = self.meta_fields or self._default_meta_fields
                for data_element in _record["data"]:
                    parsed_record = {**data_element, **{field: value for field, value in _record["meta"].items() if field in meta_fields}}
                    self.stream_slicer.update_cursor(stream_slice, last_record=parsed_record)
                    yield parsed_record
            else:
                return _record

        for record in records_generator:
            yield from update_cursor_and_get_parsed_records(record)
        else:
            last_record = self._last_records[-1] if self._last_records else None
            if last_record:
                yield from update_cursor_and_get_parsed_records(last_record)
            else:
                yield from []


@dataclass
class RailzAiIncrementalReportsRetriever(RailzAiReportsRetriever):
    _default_meta_fields = ("reportId", "startDate", "endDate")
