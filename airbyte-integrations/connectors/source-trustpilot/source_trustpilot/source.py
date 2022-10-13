#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import datetime
import json
from dataclasses import InitVar, dataclass, field
from html.parser import HTMLParser
from time import sleep
from typing import Any, Mapping, Optional, Union, Iterable
from typing import List

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.datetime import MinMaxDatetime
from airbyte_cdk.sources.declarative.datetime.datetime_parser import DatetimeParser
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.requesters.paginators import DefaultPaginator
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.stream_slicers import SingleSlice
from airbyte_cdk.sources.declarative.types import Record, StreamSlice, StreamState, Config
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource


class TrustpilotReviewsParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.__inside_reviews_script = False
        self.__reviews_script_data = None

    def handle_starttag(self, tag, attrs):
        if tag == 'script':
            attrs_map = {e[0]: e[1] for e in attrs}
            if (('type' in attrs_map) and (attrs_map['type'] == 'application/ld+json')) and \
                    (('data-business-unit-json-ld' in attrs_map) and (attrs_map['data-business-unit-json-ld'] == 'true')):
                self.__inside_reviews_script = True

    def handle_data(self, data):
        if self.__inside_reviews_script:
            self.__reviews_script_data = data

    def handle_endtag(self, tag):
        if tag == 'script':
            if self.__inside_reviews_script:
                self.__inside_reviews_script = False

    def get_reviews_script_data(self):
        return self.__reviews_script_data


@dataclass
class TrustpilotExtractor(RecordExtractor):
    """
    Extractor for Trustpilot.
    It parses output HTML and finds all `Review` occurences in it.
    """

    options: InitVar[Mapping[str, Any]]

    def __post_init__(self, options: Mapping[str, Any]):
        self._timeout_ms = options['config']['timeout_ms'] if 'timeout_ms' in options['config'] else 1000

    @staticmethod
    def __parse_html(response: requests.Response) -> List[Record]:
        dom = response.text
        parser = TrustpilotReviewsParser()
        parser.feed(dom)
        data = parser.get_reviews_script_data()
        data = json.loads(data)
        data = data['@graph']
        data = list(filter(lambda e: e.get('@type', '') == 'Review', data))
        return data

    def extract_records(self, response: requests.Response,
                        ) -> List[Record]:
        sleep(self._timeout_ms / 1000.0)
        return self.__parse_html(response)


@dataclass
class TrustpilotStreamSlicer(SingleSlice):
    """
    StreamSlicer for Trustpilot.
    Copy of SingleSlice instead of `update_curstor/get_stream_state/stream_slices` logic:
    1. `update_cursor` finds the newest review date as `new_` + stream_cursor_field.
    2. `get_stream_state` output two dates: `new_` + stream_cursor_field and `old_` + stream_cursor_field.
    3. `stream_slices` output is pretty same to `get_stream_state` output.
    """

    start_datetime: Union[MinMaxDatetime, str]
    cursor_field: Union[InterpolatedString, str]
    datetime_format: str
    config: Config

    _start_datetime_value: datetime.datetime = field(repr=False, default=None)
    _stream_slice_value: datetime.datetime = field(repr=False, default=None)
    _first_record_value: datetime.datetime = field(repr=False, default=None)

    _cursor_field_name: str = field(repr=False, default=None)
    _new_cursor_field_name: str = field(repr=False, default=None)
    _old_cursor_field_name: str = field(repr=False, default=None)

    def __post_init__(self, options: Mapping[str, Any]):
        if not isinstance(self.start_datetime, MinMaxDatetime):
            self.start_datetime = MinMaxDatetime(self.start_datetime, options)

        self._timezone = datetime.timezone.utc
        self._parser = DatetimeParser()

        if not self.start_datetime.datetime_format:
            self.start_datetime.datetime_format = self.datetime_format

        self._start_datetime_value = self.start_datetime.get_datetime(self.config)

        self.cursor_field = InterpolatedString.create(self.cursor_field, options=options)

        self._cursor_field_name = self.cursor_field.eval(self.config)
        self._new_cursor_field_name = 'new_' + self._cursor_field_name
        self._old_cursor_field_name = 'old_' + self._cursor_field_name

    def _format_datetime(self, dt: datetime.datetime):
        return self._parser.format(dt, self.datetime_format)

    def parse_date(self, date: str) -> datetime.datetime:
        return self._parser.parse(date, self.datetime_format, self._timezone)

    def update_cursor(self, stream_slice: StreamSlice, last_record: Optional[Record] = None):
        if last_record is not None:
            if self._first_record_value is None:
                tmp = last_record.get(self.cursor_field.eval(self.config))
                self._first_record_value = self.parse_date(tmp)
        elif stream_slice is not None:
            tmp = stream_slice.get(self._new_cursor_field_name)
            self._stream_slice_value = self.parse_date(tmp)

    def get_stream_state(self) -> StreamState:
        return {
            self._old_cursor_field_name: self._format_datetime(
                self._stream_slice_value if self._stream_slice_value is not None else self._start_datetime_value),

            self._new_cursor_field_name: self._format_datetime(self._first_record_value if self._first_record_value is not None else (
                self._stream_slice_value if self._stream_slice_value is not None else self._start_datetime_value
            ))
        }

    def stream_slices(self, sync_mode: SyncMode, stream_state: Mapping[str, Any]) -> Iterable[StreamSlice]:
        return [self.get_stream_state()]


@dataclass
class TrustpilotPaginator(DefaultPaginator):
    """
    Paginator for Trustpilot.
    Copy of DefaultPaginator instead of request params logic:
    1. Trustpilot API doesn't support `page_size` param, so it's removed from request params on the fly.
    2. Trustpilot API `page` param should be omitted on first page and then should start first value 2,
       so it's updated in request params on the fly.
    """

    def get_request_params(
            self,
            *,
            stream_state: Optional[StreamState] = None,
            stream_slice: Optional[StreamSlice] = None,
            next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        res = self._get_request_options(RequestOptionType.request_parameter)
        del res['page_size']
        if 'page' in res:
            res['page'] += 1
        return res


# Declarative Source
class SourceTrustpilot(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "trustpilot.yaml"})
