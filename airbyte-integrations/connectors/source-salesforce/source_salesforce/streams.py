#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import ctypes
import math
import os
import time
import urllib.parse
import uuid
from abc import ABC
from contextlib import closing
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type, Union

import backoff
import pandas as pd
import pendulum
import requests  # type: ignore[import]
from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType, SyncMode
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.cursor import Cursor
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import IsoMillisConcurrentStreamStateConverter
from airbyte_cdk.sources.streams.core import Stream, StreamData
from airbyte_cdk.sources.streams.http import HttpClient, HttpStream, HttpSubStream
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from airbyte_cdk.utils import AirbyteTracedException
from numpy import nan
from pendulum import DateTime  # type: ignore[attr-defined]
from requests import JSONDecodeError, exceptions
from requests.models import PreparedRequest

from .api import PARENT_SALESFORCE_OBJECTS, UNSUPPORTED_FILTERING_STREAMS, Salesforce
from .availability_strategy import SalesforceAvailabilityStrategy
from .exceptions import SalesforceException, TmpFileIOError
from .rate_limiting import (
    RESPONSE_CONSUMPTION_EXCEPTIONS,
    TRANSIENT_EXCEPTIONS,
    BulkNotSupportedException,
    SalesforceErrorHandler,
    default_backoff_handler,
)

# https://stackoverflow.com/a/54517228
CSV_FIELD_SIZE_LIMIT = int(ctypes.c_ulong(-1).value // 2)
csv.field_size_limit(CSV_FIELD_SIZE_LIMIT)

DEFAULT_ENCODING = "utf-8"
LOOKBACK_SECONDS = 600  # based on https://trailhead.salesforce.com/trailblazer-community/feed/0D54V00007T48TASAZ
_JOB_TRANSIENT_ERRORS_MAX_RETRY = 1


class SalesforceStream(HttpStream, ABC):
    state_converter = IsoMillisConcurrentStreamStateConverter(is_sequential_state=False)
    page_size = 2000
    transformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization)
    encoding = DEFAULT_ENCODING

    def __init__(
        self,
        sf_api: Salesforce,
        pk: str,
        stream_name: str,
        sobject_options: Mapping[str, Any] = None,
        schema: dict = None,
        start_date=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.sf_api = sf_api
        self.pk = pk
        self.stream_name = stream_name
        self.schema: Mapping[str, Any] = schema  # type: ignore[assignment]
        self.sobject_options = sobject_options
        self.start_date = self.format_start_date(start_date)
        self._http_client = HttpClient(
            self.stream_name,
            self.logger,
            session=self._session,  # no need to specific api_budget and authenticator as HttpStream sets them in self._session
            error_handler=SalesforceErrorHandler(stream_name=self.stream_name, sobject_options=self.sobject_options),
        )

    @staticmethod
    def format_start_date(start_date: Optional[str]) -> Optional[str]:
        """Transform the format `2021-07-25` into the format `2021-07-25T00:00:00Z`"""
        if start_date:
            return pendulum.parse(start_date).strftime("%Y-%m-%dT%H:%M:%SZ")  # type: ignore[attr-defined,no-any-return]
        return None

    @property
    def max_properties_length(self) -> int:
        return Salesforce.REQUEST_SIZE_LIMITS - len(self.url_base) - 2000

    @property
    def name(self) -> str:
        return self.stream_name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.pk

    @property
    def url_base(self) -> str:
        return self.sf_api.instance_url

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return SalesforceAvailabilityStrategy()

    @property
    def too_many_properties(self):
        selected_properties = self.get_json_schema().get("properties", {})
        properties_length = len(urllib.parse.quote(",".join(p for p in selected_properties)))
        return properties_length > self.max_properties_length

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["records"]

    def get_json_schema(self) -> Mapping[str, Any]:
        if not self.schema:
            self.schema = self.sf_api.generate_schema(self.name)
        return self.schema

    def get_error_display_message(self, exception: BaseException) -> Optional[str]:
        if isinstance(exception, exceptions.ConnectionError):
            return f"After {self.max_retries} retries the connector has failed with a network error. It looks like Salesforce API experienced temporary instability, please try again later."
        return super().get_error_display_message(exception)

    def get_start_date_from_state(self, stream_state: Mapping[str, Any] = None) -> pendulum.DateTime:
        if self.state_converter.is_state_message_compatible(stream_state):
            # stream_state is in the concurrent format
            if stream_state.get("slices", []):
                return stream_state["slices"][0]["end"]
        elif stream_state and not self.state_converter.is_state_message_compatible(stream_state):
            # stream_state has not been converted to the concurrent format; this is not expected
            return pendulum.parse(stream_state.get(self.cursor_field), tz="UTC")
        return pendulum.parse(self.start_date, tz="UTC")


class PropertyChunk:
    """
    Object that is used to keep track of the current state of a chunk of properties for the stream of records being synced.
    """

    properties: Mapping[str, Any]
    first_time: bool
    record_counter: int
    next_page: Optional[Mapping[str, Any]]

    def __init__(self, properties: Mapping[str, Any]):
        self.properties = properties
        self.first_time = True
        self.record_counter = 0
        self.next_page = None


class RestSalesforceStream(SalesforceStream):
    state_converter = IsoMillisConcurrentStreamStateConverter(is_sequential_state=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.primary_key or not self.too_many_properties

    def path(self, next_page_token: Mapping[str, Any] = None, **kwargs: Any) -> str:
        if next_page_token:
            """
            If `next_page_token` is set, subsequent requests use `nextRecordsUrl`.
            """
            next_token: str = next_page_token["next_token"]
            return next_token
        return f"/services/data/{self.sf_api.version}/queryAll"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        next_token = response_data.get("nextRecordsUrl")
        return {"next_token": next_token} if next_token else None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        property_chunk: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """
        Salesforce SOQL Query: https://developer.salesforce.com/docs/atlas.en-us.232.0.api_rest.meta/api_rest/dome_queryall.htm
        """
        if next_page_token:
            # If `next_page_token` is set, subsequent requests use `nextRecordsUrl`, and do not include any parameters.
            return {}

        property_chunk = property_chunk or {}
        query = f"SELECT {','.join(property_chunk.keys())} FROM {self.name} "

        if self.name in PARENT_SALESFORCE_OBJECTS:
            # add where clause: " WHERE ContentDocumentId IN ('06905000000NMXXXXX', ...)"
            parent_field = PARENT_SALESFORCE_OBJECTS[self.name]["field"]
            parent_ids = [f"'{parent_record[parent_field]}'" for parent_record in stream_slice["parents"]]
            query += f" WHERE ContentDocumentId IN ({','.join(parent_ids)})"

        if self.primary_key and self.name not in UNSUPPORTED_FILTERING_STREAMS:
            query += f"ORDER BY {self.primary_key} ASC"

        return {"q": query}

    def chunk_properties(self) -> Iterable[Mapping[str, Any]]:
        selected_properties = self.get_json_schema().get("properties", {})

        def empty_props_with_pk_if_present():
            return {self.primary_key: selected_properties[self.primary_key]} if self.primary_key else {}

        summary_length = 0
        local_properties = empty_props_with_pk_if_present()
        for property_name, value in selected_properties.items():
            current_property_length = len(urllib.parse.quote(f"{property_name},"))
            if current_property_length + summary_length >= self.max_properties_length:
                yield local_properties
                local_properties = empty_props_with_pk_if_present()
                summary_length = 0

            local_properties[property_name] = value
            summary_length += current_property_length

        if local_properties:
            yield local_properties

    @staticmethod
    def _next_chunk_id(property_chunks: Mapping[int, PropertyChunk]) -> Optional[int]:
        """
        Figure out which chunk is going to be read next.
        It should be the one with the least number of records read by the moment.
        """
        non_exhausted_chunks = {
            # We skip chunks that have already attempted a sync before and do not have a next page
            chunk_id: property_chunk.record_counter
            for chunk_id, property_chunk in property_chunks.items()
            if property_chunk.first_time or property_chunk.next_page
        }
        if not non_exhausted_chunks:
            return None
        return min(non_exhausted_chunks, key=non_exhausted_chunks.get)

    def _read_pages(
        self,
        records_generator_fn: Callable[
            [requests.PreparedRequest, requests.Response, Mapping[str, Any], Mapping[str, Any]], Iterable[StreamData]
        ],
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        stream_state = stream_state or {}
        records_by_primary_key = {}
        property_chunks: Mapping[int, PropertyChunk] = {
            index: PropertyChunk(properties=properties) for index, properties in enumerate(self.chunk_properties())
        }
        while True:
            chunk_id = self._next_chunk_id(property_chunks)
            if chunk_id is None:
                # pagination complete
                break

            property_chunk = property_chunks[chunk_id]
            request, response = self._fetch_next_page_for_chunk(
                stream_slice, stream_state, property_chunk.next_page, property_chunk.properties
            )

            # When this is the first time we're getting a chunk's records, we set this to False to be used when deciding the next chunk
            if property_chunk.first_time:
                property_chunk.first_time = False
            property_chunk.next_page = self.next_page_token(response)
            chunk_page_records = records_generator_fn(request, response, stream_state, stream_slice)
            if not self.too_many_properties:
                # this is the case when a stream has no primary key
                # (it is allowed when properties length does not exceed the maximum value)
                # so there would be a single chunk, therefore we may and should yield records immediately
                for record in chunk_page_records:
                    property_chunk.record_counter += 1
                    yield record
                continue

            # stick together different parts of records by their primary key and emit if a record is complete
            for record in chunk_page_records:
                property_chunk.record_counter += 1
                record_id = record[self.primary_key]
                if record_id not in records_by_primary_key:
                    records_by_primary_key[record_id] = (record, 1)
                    continue
                partial_record, counter = records_by_primary_key[record_id]
                partial_record.update(record)
                counter += 1
                if counter == len(property_chunks):
                    yield partial_record  # now it's complete
                    records_by_primary_key.pop(record_id)
                else:
                    records_by_primary_key[record_id] = (partial_record, counter)

        # Process what's left.
        # Because we make multiple calls to query N records (each call to fetch X properties of all the N records),
        # there's a chance that the number of records corresponding to the query may change between the calls.
        # Select 'a', 'b' from table order by pk -> returns records with ids `1`, `2`
        #   <insert smth.>
        # Select 'c', 'd' from table order by pk -> returns records with ids `1`, `3`
        # Then records `2` and `3` would be incomplete.
        # This may result in data inconsistency. We skip such records for now and log a warning message.
        incomplete_record_ids = ",".join([str(key) for key in records_by_primary_key])
        if incomplete_record_ids:
            self.logger.warning(f"Inconsistent record(s) with primary keys {incomplete_record_ids} found. Skipping them.")

        # Always return an empty generator just in case no records were ever yielded
        yield from []

    @default_backoff_handler(max_tries=5)  # FIXME remove once HttpStream relies on the HttpClient
    def _fetch_next_page_for_chunk(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        property_chunk: Mapping[str, Any] = None,
    ) -> Tuple[requests.PreparedRequest, requests.Response]:
        request_headers = self.request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        request = self._create_prepared_request(
            path=self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            headers=dict(request_headers),
            params=self.request_params(
                stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token, property_chunk=property_chunk
            ),
            json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
        )
        request_kwargs = self.request_kwargs(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        response = self._send_request(request, request_kwargs)
        return request, response


class BatchedSubStream(HttpSubStream):
    state_converter = IsoMillisConcurrentStreamStateConverter(is_sequential_state=False)
    SLICE_BATCH_SIZE = 200

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """Instead of yielding one parent record at a time, make stream slice contain a batch of parent records.

        It allows to get <SLICE_BATCH_SIZE> records by one requests (instead of only one).
        """
        batched_slice = []
        for stream_slice in super().stream_slices(sync_mode, cursor_field, stream_state):
            if len(batched_slice) == self.SLICE_BATCH_SIZE:
                yield {"parents": batched_slice}
                batched_slice = []
            batched_slice.append(stream_slice["parent"])
        if batched_slice:
            yield {"parents": batched_slice}


class RestSalesforceSubStream(BatchedSubStream, RestSalesforceStream):
    pass


class BulkSalesforceStream(SalesforceStream):
    DEFAULT_WAIT_TIMEOUT_SECONDS = 86400  # 24-hour bulk job running time
    MAX_CHECK_INTERVAL_SECONDS = 2.0
    MAX_RETRY_NUMBER = 3

    def path(self, next_page_token: Mapping[str, Any] = None, **kwargs: Any) -> str:
        return f"/services/data/{self.sf_api.version}/jobs/query"

    transformer = TypeTransformer(TransformConfig.CustomSchemaNormalization | TransformConfig.DefaultSchemaNormalization)

    def _send_http_request(self, method: str, url: str, json: dict = None, headers: dict = None, stream: bool = False):
        """
        This method should be used when you don't have to read data from the HTTP body. Else, you will have to retry when you actually read
        the response buffer (which is either by calling `json` or `iter_content`)
        """
        headers = (
            self.authenticator.get_auth_header() if not headers else headers | self.authenticator.get_auth_header()
        )  # FIXME can we remove this?
        return self._http_client.send_request(method, url, headers=headers, json=json, request_kwargs={})[1]

    @default_backoff_handler(max_tries=5, retry_on=RESPONSE_CONSUMPTION_EXCEPTIONS)
    def _create_stream_job(self, query: str, url: str) -> Optional[str]:
        json = {"operation": "queryAll", "query": query, "contentType": "CSV", "columnDelimiter": "COMMA", "lineEnding": "LF"}
        try:
            response = self._send_http_request("POST", url, json=json)
            return response.json().get("id")  # type: ignore  # based on the API, `id` will be a string
        except BulkNotSupportedException:
            return None

    def create_stream_job(self, query: str, url: str) -> Optional[str]:
        """
        docs: https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/create_job.html

        Note that we want to retry during connection issues as well. Those can occur when calling `.json()`. Even in the case of a
        connection error during a HTTPError, we will retry as else, we won't be able to take the right action.
        """
        return self._create_stream_job(query, url)

    def wait_for_job(self, url: str) -> str:
        expiration_time: DateTime = pendulum.now().add(seconds=self.DEFAULT_WAIT_TIMEOUT_SECONDS)
        job_status = "InProgress"
        delay_timeout = 0.0
        delay_cnt = 0
        job_info = None
        # minimal starting delay is 0.5 seconds.
        # this value was received empirically
        time.sleep(0.5)
        while pendulum.now() < expiration_time:
            try:
                job_info = self._send_http_request("GET", url=url).json()
            except exceptions.HTTPError as error:
                error_code, error_message = self._extract_error_code_and_message(error.response)
                if (
                    "We can't complete the action because enabled transaction security policies took too long to complete." in error_message
                    and error_code == "TXN_SECURITY_METERING_ERROR"
                ):
                    message = 'A transient authentication error occurred. To prevent future syncs from failing, assign the "Exempt from Transaction Security" user permission to the authenticated user.'
                    raise AirbyteTracedException(message=message, failure_type=FailureType.config_error, exception=error)
                else:
                    raise error
            job_id = job_info["id"]
            if job_status != job_info["state"]:
                self.logger.info(f"Job {self.name}/{job_id} status changed from {job_status} to {job_info['state']}")
            job_status = job_info["state"]
            if job_status in ["JobComplete", "Aborted", "Failed"]:
                if job_status != "JobComplete":
                    # this is only job metadata without payload
                    error_message = job_info.get("errorMessage")
                    if not error_message:
                        # not all failed response can have "errorMessage" and we need to show full response body
                        error_message = job_info
                    self.logger.error(
                        f"Job: {self.name}/{job_id}, JobStatus: {job_status}, sobject options: {self.sobject_options}, error message: '{error_message}'"
                    )
                else:
                    self.logger.info(f"Job: {self.name}/{job_id}, JobStatus: {job_status}")
                return job_status

            if delay_timeout < self.MAX_CHECK_INTERVAL_SECONDS:
                delay_timeout = 0.5 + math.exp(delay_cnt) / 1000.0
                delay_cnt += 1

            time.sleep(delay_timeout)
            self.logger.debug(
                f"Sleeping {delay_timeout} seconds while waiting for Job: {self.name}/{job_id} to complete. Current state: {job_status}"
            )

        self.logger.warning(f"Not wait the {self.name} data for {self.DEFAULT_WAIT_TIMEOUT_SECONDS} seconds, data: {job_info}!!")
        return job_status

    def _extract_error_code_and_message(self, response: requests.Response) -> tuple[Optional[str], str]:
        try:
            error_data = response.json()[0]
            return error_data.get("errorCode"), error_data.get("message", "")
        except exceptions.JSONDecodeError:
            self.logger.warning(f"The response for `{response.request.url}` is not a JSON but was `{response.content}`")
        except IndexError:
            self.logger.warning(
                f"The response for `{response.request.url}` was expected to be a list with at least one element but was `{response.content}`"
            )

        return None, ""

    def execute_job(self, query: str, url: str) -> Tuple[Optional[str], Optional[str]]:
        job_status = "Failed"
        for i in range(0, self.MAX_RETRY_NUMBER):
            job_id = self.create_stream_job(query=query, url=url)
            if not job_id:
                return None, job_status
            job_full_url = f"{url}/{job_id}"
            self.logger.info(f"Job: {self.name}/{job_id} created, Job Full Url: {job_full_url}")
            job_status = self.wait_for_job(url=job_full_url)
            if job_status not in ["UploadComplete", "InProgress"]:
                break
            self.logger.error(f"Waiting error. Try to run this job again {i + 1}/{self.MAX_RETRY_NUMBER}...")
            self.abort_job(url=job_full_url)
            job_status = "Aborted"

        if job_status in ["Aborted", "Failed"]:
            self.delete_job(url=job_full_url)
            return None, job_status
        return job_full_url, job_status

    def filter_null_bytes(self, b: bytes):
        """
        https://github.com/airbytehq/airbyte/issues/8300
        """
        res = b.replace(b"\x00", b"")
        if len(res) < len(b):
            self.logger.warning("Filter 'null' bytes from string, size reduced %d -> %d chars", len(b), len(res))
        return res

    def get_response_encoding(self, headers) -> str:
        """Returns encodings from given HTTP Header Dict.

        :param headers: dictionary to extract encoding from.
        :rtype: str
        """

        content_type = headers.get("content-type")

        if not content_type:
            return self.encoding

        content_type, params = requests.utils._parse_content_type_header(content_type)

        if "charset" in params:
            return params["charset"].strip("'\"")

        return self.encoding

    @default_backoff_handler(
        max_tries=5, retry_on=RESPONSE_CONSUMPTION_EXCEPTIONS
    )  # We need the default_backoff_handler here because the HttpClient does not handle errors during the streaming of the response
    def download_data(self, url: str, chunk_size: int = 1024) -> tuple[str, str, dict]:
        """
        Retrieves binary data result from successfully `executed_job`, using chunks, to avoid local memory limitations.
        @ url: string - the url of the `executed_job`
        @ chunk_size: int - the buffer size for each chunk to fetch from stream, in bytes, default: 1024 bytes
        Return the tuple containing string with file path of downloaded binary data (Saved temporarily) and file encoding.
        """
        # set filepath for binary data from response
        tmp_file = str(uuid.uuid4())
        _, streamed_response = self._http_client.send_request(
            "GET", url, headers={"Accept-Encoding": "gzip"}, request_kwargs={"stream": True}
        )
        with closing(streamed_response) as response, open(tmp_file, "wb") as data_file:
            response_headers = response.headers
            response_encoding = self.get_response_encoding(response_headers)
            for chunk in response.iter_content(chunk_size=chunk_size):
                data_file.write(self.filter_null_bytes(chunk))
        # check the file exists
        if os.path.isfile(tmp_file):
            return tmp_file, response_encoding, response_headers
        else:
            raise TmpFileIOError(f"The IO/Error occured while verifying binary data. Stream: {self.name}, file {tmp_file} doesn't exist.")

    def read_with_chunks(self, path: str, file_encoding: str, chunk_size: int = 100) -> Iterable[Tuple[int, Mapping[str, Any]]]:
        """
        Reads the downloaded binary data, using lines chunks, set by `chunk_size`.
        @ path: string - the path to the downloaded temporarily binary data.
        @ file_encoding: string - encoding for binary data file according to Standard Encodings from codecs module
        @ chunk_size: int - the number of lines to read at a time, default: 100 lines / time.
        """
        try:
            with open(path, "r", encoding=file_encoding) as data:
                chunks = pd.read_csv(data, chunksize=chunk_size, iterator=True, dialect="unix", dtype=object)
                for chunk in chunks:
                    chunk = chunk.replace({nan: None}).to_dict(orient="records")
                    for row in chunk:
                        yield row
        except pd.errors.EmptyDataError as e:
            self.logger.info(f"Empty data received. {e}")
            yield from []
        except IOError as ioe:
            raise TmpFileIOError(f"The IO/Error occured while reading tmp data. Called: {path}. Stream: {self.name}", ioe)
        finally:
            # remove binary tmp file, after data is read
            os.remove(path)

    def abort_job(self, url: str):
        data = {"state": "Aborted"}
        self._send_http_request("PATCH", url=url, json=data)
        self.logger.warning("Broken job was aborted")

    def delete_job(self, url: str):
        self._send_http_request("DELETE", url=url)

    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return None

    def next_page_token(self, last_record: Mapping[str, Any]) -> Optional[Mapping[str, Any]]:
        return None

    def get_query_select_fields(self) -> str:
        return ", ".join(
            {
                key: value
                for key, value in self.get_json_schema().get("properties", {}).items()
                if value.get("format") != "base64" and "object" not in value["type"]
            }
        )

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """
        Salesforce SOQL Query: https://developer.salesforce.com/docs/atlas.en-us.232.0.api_rest.meta/api_rest/dome_queryall.htm
        """

        select_fields = self.get_query_select_fields()
        query = f"SELECT {select_fields} FROM {self.name}"
        if next_page_token:
            query += next_page_token["next_token"]

        if self.name in PARENT_SALESFORCE_OBJECTS:
            # add where clause: " WHERE ContentDocumentId IN ('06905000000NMXXXXX', '06905000000Mxp7XXX', ...)"
            parent_field = PARENT_SALESFORCE_OBJECTS[self.name]["field"]
            parent_ids = [f"'{parent_record[parent_field]}'" for parent_record in stream_slice["parents"]]
            query += f" WHERE ContentDocumentId IN ({','.join(parent_ids)})"

        return {"q": query}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
        call_count: int = 0,
    ) -> Iterable[Mapping[str, Any]]:
        stream_state = stream_state or {}
        next_page_token = None

        params = self.request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        path = self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        job_full_url, job_status = self.execute_job(query=params["q"], url=f"{self.url_base}{path}")
        if not job_full_url:
            if job_status == "Failed":
                # As rule as BULK logic returns unhandled error. For instance:
                # error message: 'Unexpected exception encountered in query processing.
                #                 Please contact support with the following id: 326566388-63578 (-436445966)'"
                # Thus we can try to switch to GET sync request because its response returns obvious error message
                standard_instance = self.get_standard_instance()
                self.logger.warning("switch to STANDARD(non-BULK) sync. Because the SalesForce BULK job has returned a failed status")
                stream_is_available, error = standard_instance.check_availability(self.logger, None)
                if not stream_is_available:
                    self.logger.warning(f"Skipped syncing stream '{standard_instance.name}' because it was unavailable. Error: {error}")
                    return
                yield from standard_instance.read_records(
                    sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
                )
                return
            raise SalesforceException(f"Job for {self.name} stream using BULK API was failed.")
        salesforce_bulk_api_locator = None
        while True:
            req = PreparedRequest()
            req.prepare_url(f"{job_full_url}/results", {"locator": salesforce_bulk_api_locator})
            try:
                tmp_file, response_encoding, response_headers = self.download_data(url=req.url)
            except TRANSIENT_EXCEPTIONS as exception:
                # We have seen some cases where pulling the job result's data would simply not work even with the retry on `download_data`.
                # Those cases have unfortunately not been documented and we are unsure of the efficacy of retrying the whole job as we have
                # done multiple reliability change without tracking the efficacy of each.
                if call_count >= _JOB_TRANSIENT_ERRORS_MAX_RETRY:
                    self.logger.error(f"Downloading data failed even after {call_count} retries. Stopping retry and raising exception")
                    raise exception
                self.logger.warning(f"Downloading data failed after {call_count} retries. Retrying the whole job...")
                call_count += 1
                yield from self.read_records(sync_mode, cursor_field, stream_slice, stream_state, call_count=call_count)
                return

            for record in self.read_with_chunks(tmp_file, response_encoding):
                yield record

            if response_headers.get("Sforce-Locator", "null") == "null":
                break
            salesforce_bulk_api_locator = response_headers.get("Sforce-Locator")
        self.delete_job(url=job_full_url)

    def get_standard_instance(self) -> SalesforceStream:
        """Returns a instance of standard logic(non-BULK) with same settings"""
        stream_kwargs = dict(
            sf_api=self.sf_api,
            pk=self.pk,
            stream_name=self.stream_name,
            schema=self.schema,
            sobject_options=self.sobject_options,
            authenticator=self._session.auth,
        )
        new_cls: Type[SalesforceStream] = RestSalesforceStream
        if isinstance(self, BulkIncrementalSalesforceStream):
            stream_kwargs.update({"replication_key": self.replication_key, "start_date": self.start_date})
            new_cls = IncrementalRestSalesforceStream

        standard_instance = new_cls(**stream_kwargs)
        if hasattr(standard_instance, "set_cursor"):
            standard_instance.set_cursor(self._stream_slicer_cursor)
        return standard_instance


class BulkSalesforceSubStream(BatchedSubStream, BulkSalesforceStream):
    pass


@BulkSalesforceStream.transformer.registerCustomTransform
def transform_empty_string_to_none(instance: Any, schema: Any):
    """
    BULK API returns a `csv` file, where all values are initially as string type.
    This custom transformer replaces empty lines with `None` value.
    """
    if isinstance(instance, str) and not instance.strip():
        instance = None

    return instance


class IncrementalRestSalesforceStream(RestSalesforceStream, ABC):
    state_checkpoint_interval = 500
    _slice = None

    def __init__(self, replication_key: str, stream_slice_step: str = "P30D", **kwargs):
        super().__init__(**kwargs)
        self.replication_key = replication_key
        self._stream_slice_step = stream_slice_step
        self._stream_slicer_cursor = None

    def set_cursor(self, cursor: Cursor) -> None:
        self._stream_slicer_cursor = cursor

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if not self._stream_slicer_cursor:
            raise ValueError("Cursor should be set at this point")

        for slice_start, slice_end in self._stream_slicer_cursor.generate_slices():
            yield {
                "start_date": slice_start.isoformat(timespec="milliseconds"),
                "end_date": slice_end.isoformat(timespec="milliseconds"),
            }

    @property
    def stream_slice_step(self) -> pendulum.Duration:
        return pendulum.parse(self._stream_slice_step)

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
        property_chunk: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        if next_page_token:
            """
            If `next_page_token` is set, subsequent requests use `nextRecordsUrl`, and do not include any parameters.
            """
            return {}

        property_chunk = property_chunk or {}

        start_date = max(
            (stream_state or {}).get(self.cursor_field, self.start_date),
            (stream_slice or {}).get("start_date", ""),
            (next_page_token or {}).get("start_date", ""),
        )
        end_date = (stream_slice or {}).get("end_date", pendulum.now(tz="UTC").isoformat(timespec="milliseconds"))

        select_fields = ",".join(property_chunk.keys())
        table_name = self.name
        where_conditions = []

        if start_date:
            where_conditions.append(f"{self.cursor_field} >= {start_date}")
        if end_date:
            where_conditions.append(f"{self.cursor_field} < {end_date}")

        where_clause = f"WHERE {' AND '.join(where_conditions)}"
        query = f"SELECT {select_fields} FROM {table_name} {where_clause}"

        return {"q": query}

    @property
    def cursor_field(self) -> str:
        return self.replication_key

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Return the latest state by comparing the cursor value in the latest record with the stream's most recent state
        object and returning an updated state object. Check if latest record is IN stream slice interval => ignore if not
        """
        latest_record_value: pendulum.DateTime = pendulum.parse(latest_record[self.cursor_field])
        slice_max_value: pendulum.DateTime = pendulum.parse(self._slice.get("end_date"))
        max_possible_value = min(latest_record_value, slice_max_value)
        if current_stream_state.get(self.cursor_field):
            if latest_record_value > slice_max_value:
                return {self.cursor_field: max_possible_value.isoformat()}
            max_possible_value = max(latest_record_value, pendulum.parse(current_stream_state[self.cursor_field]))
        return {self.cursor_field: max_possible_value.isoformat()}


class BulkIncrementalSalesforceStream(BulkSalesforceStream, IncrementalRestSalesforceStream):
    state_checkpoint_interval = None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        start_date = stream_slice["start_date"]
        end_date = stream_slice["end_date"]

        select_fields = self.get_query_select_fields()
        table_name = self.name
        where_conditions = [f"{self.cursor_field} >= {start_date}", f"{self.cursor_field} < {end_date}"]

        where_clause = f"WHERE {' AND '.join(where_conditions)}"
        query = f"SELECT {select_fields} FROM {table_name} {where_clause}"
        return {"q": query}


class Describe(Stream):
    state_converter = IsoMillisConcurrentStreamStateConverter(is_sequential_state=False)
    """
    Stream of sObjects' (Salesforce Objects) describe:
    https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm
    """

    name = "Describe"
    primary_key = "name"

    def __init__(self, sf_api: Salesforce, catalog: ConfiguredAirbyteCatalog = None, **kwargs):
        super().__init__(**kwargs)
        self.sf_api = sf_api
        if catalog:
            self.sobjects_to_describe = [s.stream.name for s in catalog.streams if s.stream.name != self.name]

    def read_records(self, **kwargs) -> Iterable[Mapping[str, Any]]:
        """
        Yield describe response of SObjects defined in catalog as streams only.
        """
        for sobject in self.sobjects_to_describe:
            yield self.sf_api.describe(sobject=sobject)
