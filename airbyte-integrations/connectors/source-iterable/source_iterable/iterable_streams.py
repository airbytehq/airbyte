#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from abc import ABC, abstractmethod
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from pendulum.datetime import DateTime
from requests.exceptions import ChunkedEncodingError
from source_iterable.slice_generators import AdjustableSliceGenerator, RangeSliceGenerator, StreamSlice


class IterableStream(HttpStream, ABC):

    # Hardcode the value because it is not returned from the API
    BACKOFF_TIME_CONSTANT = 10.0
    # define date-time fields with potential wrong format

    url_base = "https://api.iterable.com/api/"
    primary_key = "id"

    def __init__(self, authenticator):
        self._cred = authenticator
        super().__init__(authenticator)

    @property
    @abstractmethod
    def data_field(self) -> str:
        """
        :return: Default field name to get data from response
        """

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        return self.BACKOFF_TIME_CONSTANT

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Iterable API does not support pagination
        """
        return None

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        response_json = response.json()
        records = response_json.get(self.data_field, [])

        for record in records:
            yield record


class IterableExportStream(IterableStream, ABC):
    """
    This stream utilize "export" Iterable api for getting large amount of data.
    It can return data in form of new line separater strings each of each
    representing json object.
    Data could be windowed by date ranges by applying startDateTime and
    endDateTime parameters.  Single request could return large volumes of data
    and request rate is limited by 4 requests per minute.

    Details: https://api.iterable.com/api/docs#export_exportDataJson
    """

    cursor_field = "createdAt"
    primary_key = None

    def __init__(self, start_date=None, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.parse(start_date)
        self.stream_params = {"dataTypeName": self.data_field}

    def path(self, **kwargs) -> str:
        return "export/data.json"

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        # Use default exponential backoff
        return None

    # For python backoff package expo backoff delays calculated according to formula:
    # delay = factor * base ** n where base is 2
    # With default factor equal to 5 and 5 retries delays would be 5, 10, 20, 40 and 80 seconds.
    # For exports stream there is a limit of 4 requests per minute.
    # Tune up factor and retries to send a lot of excessive requests before timeout exceed.
    @property
    def retry_factor(self) -> int:
        return 20

    # With factor 20 it woud be 20, 40, 80 and 160 seconds delays.
    @property
    def max_retries(self) -> Union[int, None]:
        return 4

    @staticmethod
    def _field_to_datetime(value: Union[int, str]) -> pendulum.datetime:
        if isinstance(value, int):
            value = pendulum.from_timestamp(value / 1000.0)
        elif isinstance(value, str):
            value = pendulum.parse(value, strict=False)
        else:
            raise ValueError(f"Unsupported type of datetime field {type(value)}")
        return value

    def get_updated_state(
        self,
        current_stream_state: MutableMapping[str, Any],
        latest_record: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state object
        and returning an updated state object.
        """
        latest_benchmark = latest_record[self.cursor_field]
        if current_stream_state.get(self.cursor_field):
            return {
                self.cursor_field: str(
                    max(
                        latest_benchmark,
                        self._field_to_datetime(current_stream_state[self.cursor_field]),
                    )
                )
            }
        return {self.cursor_field: str(latest_benchmark)}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: StreamSlice,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:

        params = super().request_params(stream_state=stream_state)
        params.update(
            {
                "startDateTime": stream_slice.start_date.strftime("%Y-%m-%d %H:%M:%S"),
                "endDateTime": stream_slice.end_date.strftime("%Y-%m-%d %H:%M:%S"),
            },
            **self.stream_params,
        )
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for obj in response.iter_lines():
            record = json.loads(obj)
            record[self.cursor_field] = self._field_to_datetime(record[self.cursor_field])
            yield record

    def request_kwargs(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Mapping[str, Any]:
        """
        https://api.iterable.com/api/docs#export_exportDataJson
        Sending those type of requests could download large piece of json
        objects splitted with newline character.
        Passing stream=True argument to requests.session.send method to avoid
        loading whole analytics report content into memory.
        """
        return {"stream": True}

    def get_start_date(self, stream_state: Mapping[str, Any]) -> DateTime:
        stream_state = stream_state or {}
        start_datetime = self._start_date
        if stream_state.get(self.cursor_field):
            start_datetime = pendulum.parse(stream_state[self.cursor_field])
        return start_datetime

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[StreamSlice]]:

        start_datetime = self.get_start_date(stream_state)
        return [StreamSlice(start_datetime, pendulum.now("UTC"))]


class IterableExportStreamRanged(IterableExportStream):
    """
    This class use RangeSliceGenerator class to break single request into
    ranges with same (or less for final range) number of days. By default it 90
    days.
    """

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[StreamSlice]]:

        start_datetime = self.get_start_date(stream_state)

        return RangeSliceGenerator(start_datetime)


class IterableExportStreamAdjustableRange(IterableExportStream):
    """
    For streams that could produce large amount of data in single request so we
    cant just use IterableExportStreamRanged to split it in even ranges. If
    request processing takes a lot of time API server could just close
    connection and connector code would fail with ChunkedEncodingError.

    To solve this problem we use AdjustableSliceGenerator that able to adjust
    next slice range based on two factor:
    1. Previous slice range / time to process ratio.
    2. Had previous request failed with ChunkedEncodingError

    In case of slice processing request failed with ChunkedEncodingError (which
    means that API server closed connection cause of request takes to much
    time) make CHUNKED_ENCODING_ERROR_RETRIES (3) retries each time reducing
    slice length.

    See AdjustableSliceGenerator description for more details on next slice length adjustment alghorithm.
    """

    _adjustable_generator: AdjustableSliceGenerator = None
    CHUNKED_ENCODING_ERROR_RETRIES = 3

    def stream_slices(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Optional[StreamSlice]]:

        start_datetime = self.get_start_date(stream_state)
        self._adjustable_generator = AdjustableSliceGenerator(start_datetime)
        return self._adjustable_generator

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str],
        stream_slice: StreamSlice,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        start_time = pendulum.now()
        for _ in range(self.CHUNKED_ENCODING_ERROR_RETRIES):
            try:

                self.logger.info(
                    f"Processing slice of {(stream_slice.end_date - stream_slice.start_date).total_days()} days for stream {self.name}"
                )
                for record in super().read_records(
                    sync_mode=sync_mode,
                    cursor_field=cursor_field,
                    stream_slice=stream_slice,
                    stream_state=stream_state,
                ):
                    now = pendulum.now()
                    self._adjustable_generator.adjust_range(now - start_time)
                    yield record
                    start_time = now
                break
            except ChunkedEncodingError:
                self.logger.warn("ChunkedEncodingError occured, decrease days range and try again")
                stream_slice = self._adjustable_generator.reduce_range()
        else:
            raise Exception(f"ChunkedEncodingError: Reached maximum number of retires: {self.CHUNKED_ENCODING_ERROR_RETRIES}")
