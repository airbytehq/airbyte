#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import csv
import ctypes
import urllib.parse
from abc import ABC
from datetime import timedelta
from typing import Any, Callable, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type, Union

import pendulum
import requests  # type: ignore[import]
from airbyte_cdk import (
    BearerAuthenticator,
    CursorPaginationStrategy,
    DeclarativeStream,
    DefaultPaginator,
    DpathExtractor,
    HttpMethod,
    HttpRequester,
    JsonDecoder,
    MessageRepository,
    RecordSelector,
    RequestOption,
    RequestOptionType,
    SimpleRetriever,
    StreamSlice,
)
from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode
from airbyte_cdk.sources.declarative.async_job.job_orchestrator import AsyncJobOrchestrator
from airbyte_cdk.sources.declarative.async_job.job_tracker import JobTracker
from airbyte_cdk.sources.declarative.async_job.status import AsyncJobStatus
from airbyte_cdk.sources.declarative.auth.token_provider import InterpolatedStringTokenProvider
from airbyte_cdk.sources.declarative.decoders import NoopDecoder
from airbyte_cdk.sources.declarative.extractors import ResponseToFileExtractor
from airbyte_cdk.sources.declarative.requesters.http_job_repository import AsyncHttpJobRepository
from airbyte_cdk.sources.declarative.requesters.request_options import InterpolatedRequestOptionsProvider
from airbyte_cdk.sources.declarative.retrievers import AsyncRetriever
from airbyte_cdk.sources.declarative.schema import InlineSchemaLoader
from airbyte_cdk.sources.declarative.stream_slicers import StreamSlicer
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.concurrent.cursor import ConcurrentCursor
from airbyte_cdk.sources.streams.concurrent.state_converters.datetime_stream_state_converter import IsoMillisConcurrentStreamStateConverter
from airbyte_cdk.sources.streams.core import CheckpointMixin, Stream, StreamData
from airbyte_cdk.sources.streams.http import HttpClient, HttpStream, HttpSubStream
from airbyte_cdk.sources.types import StreamState
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from pendulum import DateTime  # type: ignore[attr-defined]
from requests import exceptions

from .api import PARENT_SALESFORCE_OBJECTS, UNSUPPORTED_FILTERING_STREAMS, Salesforce
from .availability_strategy import SalesforceAvailabilityStrategy
from .rate_limiting import BulkNotSupportedException, SalesforceErrorHandler, default_backoff_handler

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
        job_tracker: JobTracker,
        message_repository: MessageRepository,
        sobject_options: Mapping[str, Any] = None,
        schema: dict = None,
        start_date=None,
        **kwargs,
    ):
        self.stream_name = stream_name
        self.pk = pk
        self.sf_api = sf_api
        super().__init__(**kwargs)
        self.schema: Mapping[str, Any] = schema  # type: ignore[assignment]
        self.sobject_options = sobject_options
        self.start_date = self.format_start_date(start_date)
        self._job_tracker = job_tracker
        self._message_repository = message_repository
        self._http_client = HttpClient(
            self.stream_name,
            self.logger,
            session=self._http_client._session,  # no need to specific api_budget and authenticator as HttpStream sets them in self._session
            error_handler=SalesforceErrorHandler(stream_name=self.stream_name, sobject_options=self.sobject_options),
        )

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        """
        In order to avoid RFR which does uses `_read_single_page` instead of `_read_pages`
        """
        yield from super().read_records(sync_mode, cursor_field, stream_slice, stream_state)

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
        return self._http_client.send_request(
            http_method=self.http_method,
            url=self._join_url(
                self.url_base,
                self.path(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            ),
            headers=dict(request_headers),
            params=self.request_params(
                stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token, property_chunk=property_chunk
            ),
            json=self.request_body_json(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            data=self.request_body_data(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token),
            request_kwargs={},
        )


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


class BulkDatetimeStreamSlicer(StreamSlicer):
    def __init__(self, cursor: Optional[ConcurrentCursor]) -> None:
        self._cursor = cursor

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        return {}

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def stream_slices(self) -> Iterable[StreamSlice]:
        if not self._cursor:
            yield from [StreamSlice(partition={}, cursor_slice={})]
            return

        for slice_start, slice_end in self._cursor.generate_slices():
            yield StreamSlice(
                partition={},
                cursor_slice={
                    "start_date": slice_start.isoformat(timespec="milliseconds"),
                    "end_date": slice_end.isoformat(timespec="milliseconds"),
                },
            )


class BulkParentStreamStreamSlicer(StreamSlicer):
    def __init__(
        self,
        batched_substream: BatchedSubStream,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]],
        stream_state: Optional[Mapping[str, Any]],
        parend_id_field: str,
    ) -> None:
        self._batched_substream = batched_substream
        self._sync_mode = sync_mode
        self._cursor_field = cursor_field
        self._stream_state = stream_state
        self._parend_id_field = parend_id_field

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def get_request_body_data(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Union[Mapping[str, Any], str]:
        return {}

    def get_request_body_json(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        return {}

    def stream_slices(self) -> Iterable[StreamSlice]:
        for batched_parents in self._batched_substream.stream_slices(
            sync_mode=self._sync_mode, cursor_field=self._cursor_field, stream_state=self._stream_state
        ):
            yield StreamSlice(
                partition={"parents": [parent[self._parend_id_field] for parent in batched_parents["parents"]]}, cursor_slice={}
            )


class BulkSalesforceStream(SalesforceStream):
    def __init__(self, **kwargs) -> None:
        self._stream_slicer_cursor = None
        self._switch_from_bulk_to_rest = False
        self._rest_stream = None
        super().__init__(**kwargs)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        This method needs to be there as `HttpStream.next_page_token` is abstract but it will never get called
        """
        pass

    def path(self, next_page_token: Mapping[str, Any] = None, **kwargs: Any) -> str:
        """
        This method needs to be there as `HttpStream.path` is abstract but it will never get called
        """
        pass

    def _instantiate_declarative_stream(self, stream_slicer: StreamSlicer, has_bulk_parent: bool) -> None:
        """
        For streams with a replication key and where filtering is supported, we need to have the cursor in order to instantiate the
        DeclarativeStream hence why this isn't called in the __init__
        """
        config = {}
        parameters = {}
        url_base = self.sf_api.instance_url
        job_query_path = f"/services/data/{self.sf_api.version}/jobs/query"
        decoder = JsonDecoder(parameters=parameters)
        authenticator = BearerAuthenticator(
            token_provider=InterpolatedStringTokenProvider(api_token=self.sf_api.access_token, config=config, parameters=parameters),
            config=config,
            parameters=parameters,
        )
        error_handler = SalesforceErrorHandler()
        select_fields = self.get_query_select_fields()
        query = f"SELECT {select_fields} FROM {self.name}"  # FIXME "def request_params" is also handling `next_token` (I don't know why, I think it's always None) and parent streams
        if self.cursor_field:
            where_in_query = '{{ " WHERE " if stream_slice["start_date"] or stream_slice["end_date"] else "" }}'
            lower_boundary_interpolation = (
                '{{ "' f"{self.cursor_field}" ' >= " + stream_slice["start_date"] if stream_slice["start_date"] else "" }}'
            )
            and_keyword_interpolation = '{{" AND " if stream_slice["start_date"] and stream_slice["end_date"] else "" }}'
            upper_boundary_interpolation = (
                '{{ "' f"{self.cursor_field}" ' < " + stream_slice["end_date"] if stream_slice["end_date"] else "" }}'
            )
            query = query + where_in_query + lower_boundary_interpolation + and_keyword_interpolation + upper_boundary_interpolation
        elif isinstance(stream_slicer, BulkParentStreamStreamSlicer):
            where_in_query = " WHERE ContentDocumentId IN ('"
            parents_interpolation = '{{ "\', \'".join(stream_slice["parents"]) }}'
            closing_parenthesis = "')"
            query = query + where_in_query + parents_interpolation + closing_parenthesis
        creation_requester = HttpRequester(
            name=f"{self.name} - creation requester",
            url_base=url_base,
            path=job_query_path,
            authenticator=authenticator,
            error_handler=error_handler,
            http_method=HttpMethod.POST,
            request_options_provider=InterpolatedRequestOptionsProvider(
                request_body_data=None,
                request_body_json={
                    "operation": "queryAll",
                    "query": query,
                    "contentType": "CSV",
                    "columnDelimiter": "COMMA",
                    "lineEnding": "LF",
                },
                request_headers=None,
                request_parameters=None,
                config=config,
                parameters=parameters,
            ),
            config=config,
            parameters=parameters,
            disable_retries=False,
            message_repository=self._message_repository,
            use_cache=False,
            decoder=decoder,
            stream_response=False,
        )
        polling_id_interpolation = "{{stream_slice['create_job_response'].json()['id'] }}"
        polling_requester = HttpRequester(
            name=f"{self.name} - polling requester",
            url_base=url_base,
            path=f"{job_query_path}/{polling_id_interpolation}",
            authenticator=authenticator,
            error_handler=error_handler,
            http_method=HttpMethod.GET,
            request_options_provider=InterpolatedRequestOptionsProvider(
                request_body_data=None,
                request_body_json=None,
                request_headers=None,
                request_parameters=None,
                config=config,
                parameters=parameters,
            ),
            config=config,
            parameters=parameters,
            disable_retries=False,
            message_repository=self._message_repository,
            use_cache=False,
            decoder=decoder,
            stream_response=False,
        )
        # "GET", url, headers = {"Accept-Encoding": "gzip"}, request_kwargs = {"stream": True}
        download_id_interpolation = "{{stream_slice['url']}}"
        job_download_components_name = f"{self.name} - download requester"
        download_requester = HttpRequester(
            name=job_download_components_name,
            url_base=url_base,
            path=f"{job_query_path}/{download_id_interpolation}/results",
            authenticator=authenticator,
            error_handler=error_handler,
            http_method=HttpMethod.GET,
            request_options_provider=InterpolatedRequestOptionsProvider(
                request_body_data=None,
                request_body_json=None,
                request_headers={"Accept-Encoding": "gzip"},
                request_parameters=None,
                config=config,
                parameters=parameters,
            ),
            config=config,
            parameters=parameters,
            disable_retries=False,
            message_repository=self._message_repository,
            use_cache=False,
            stream_response=True,
        )
        download_retriever = SimpleRetriever(
            requester=download_requester,
            record_selector=RecordSelector(
                extractor=ResponseToFileExtractor(),
                record_filter=None,
                transformations=[],
                schema_normalization=TypeTransformer(TransformConfig.NoTransform),
                config=config,
                parameters={},
            ),
            primary_key=None,
            name=job_download_components_name,
            paginator=DefaultPaginator(
                decoder=NoopDecoder(),
                page_size_option=None,
                page_token_option=RequestOption(
                    field_name="locator",
                    inject_into=RequestOptionType.request_parameter,
                    parameters={},
                ),
                pagination_strategy=CursorPaginationStrategy(
                    cursor_value="{{ headers['Sforce-Locator'] }}",
                    stop_condition="{{ headers.get('Sforce-Locator', None) == 'null' or not headers.get('Sforce-Locator', None) }}",
                    decoder=NoopDecoder(),
                    config=config,
                    parameters={},
                ),
                url_base=url_base,
                config=config,
                parameters={},
            ),
            config=config,
            parameters={},
        )

        abort_requester = HttpRequester(
            name=f"{self.name} - abort requester",
            url_base=url_base,
            path=f"{job_query_path}/{polling_id_interpolation}",
            authenticator=authenticator,
            error_handler=error_handler,
            http_method=HttpMethod.PATCH,
            request_options_provider=InterpolatedRequestOptionsProvider(
                request_body_data=None,
                request_body_json={"state": "Aborted"},
                request_headers=None,
                request_parameters=None,
                config=config,
                parameters=parameters,
            ),
            config=config,
            parameters=parameters,
            disable_retries=False,
            message_repository=self._message_repository,
            use_cache=False,
            stream_response=False,
        )
        delete_requester = HttpRequester(
            name=f"{self.name} - delete requester",
            url_base=url_base,
            path=f"{job_query_path}/{polling_id_interpolation}",
            authenticator=authenticator,
            error_handler=error_handler,
            http_method=HttpMethod.DELETE,
            request_options_provider=None,
            config=config,
            parameters=parameters,
            disable_retries=False,
            message_repository=self._message_repository,
            use_cache=False,
            stream_response=False,
        )
        status_extractor = DpathExtractor(decoder=JsonDecoder(parameters={}), field_path=["state"], config={}, parameters={})
        urls_extractor = DpathExtractor(decoder=JsonDecoder(parameters={}), field_path=["id"], config={}, parameters={})
        job_repository = AsyncHttpJobRepository(
            creation_requester=creation_requester,
            polling_requester=polling_requester,
            download_retriever=download_retriever,
            abort_requester=abort_requester,
            delete_requester=delete_requester,
            status_extractor=status_extractor,
            status_mapping={
                "InProgress": AsyncJobStatus.RUNNING,
                "UploadComplete": AsyncJobStatus.RUNNING,
                "JobComplete": AsyncJobStatus.COMPLETED,
                "Aborted": AsyncJobStatus.FAILED,
                "Failed": AsyncJobStatus.FAILED,
            },
            urls_extractor=urls_extractor,
            job_timeout=self.DEFAULT_WAIT_TIMEOUT,
        )
        record_selector = RecordSelector(
            extractor=None,  # FIXME typing won't like that but it is not used
            record_filter=None,
            transformations=[],
            schema_normalization=self.transformer,
            config=config,
            parameters=parameters,
        )
        self._bulk_job_stream = DeclarativeStream(
            retriever=AsyncRetriever(
                config={},
                parameters={},
                record_selector=record_selector,
                stream_slicer=stream_slicer,
                job_orchestrator_factory=lambda stream_slices: AsyncJobOrchestrator(
                    job_repository,
                    stream_slices,
                    self._job_tracker,
                    self._message_repository,
                    exceptions_to_break_on=[BulkNotSupportedException],
                    has_bulk_parent=has_bulk_parent,
                ),
            ),
            config={},
            parameters={},
            name=self.name,
            primary_key=self.pk,
            schema_loader=InlineSchemaLoader({}, {}),  # FIXME call get_json_schema?
            # the interface mentions that this is Optional,
            # but I get `'NoneType' object has no attribute 'eval'` by passing None
            stream_cursor_field="",
        )

    DEFAULT_WAIT_TIMEOUT = timedelta(hours=24)
    MAX_CHECK_INTERVAL_SECONDS = 2.0
    MAX_RETRY_NUMBER = 3

    transformer = TypeTransformer(TransformConfig.CustomSchemaNormalization | TransformConfig.DefaultSchemaNormalization)

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
        if self._is_async_job_slice(stream_slice):
            if self._switch_from_bulk_to_rest:
                # ignore as we have switched to rest
                pass
            else:
                yield from self._bulk_job_stream.read_records(sync_mode, cursor_field, stream_slice, stream_state)
        else:
            yield from self._rest_stream.read_records(sync_mode, cursor_field, stream_slice, stream_state)

    def _is_async_job_slice(self, stream_slice):
        return isinstance(stream_slice, StreamSlice) and "partition" in stream_slice.partition

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self._instantiate_declarative_stream(BulkDatetimeStreamSlicer(self._stream_slicer_cursor), has_bulk_parent=False)
        try:
            yield from self._bulk_job_stream.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        except BulkNotSupportedException:
            self.logger.warning(
                "attempt to switch to STANDARD(non-BULK) sync. Because the SalesForce BULK job has returned a failed status"
            )
            self._switch_from_bulk_to_rest = True
            self._rest_stream = self.get_standard_instance()
            stream_is_available, error = SalesforceAvailabilityStrategy().check_availability(self._rest_stream, self.logger, None)
            if not stream_is_available:
                self.logger.warning(f"Skipped syncing stream '{self._rest_stream.name}' because it was unavailable. Error: {error}")
                yield from []
            else:
                yield from self._rest_stream.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)

    def get_standard_instance(self) -> SalesforceStream:
        """Returns a instance of standard logic(non-BULK) with same settings"""
        stream_kwargs = dict(
            sf_api=self.sf_api,
            pk=self.pk,
            stream_name=self.stream_name,
            schema=self.schema,
            sobject_options=self.sobject_options,
            authenticator=self._http_client._session.auth,
            job_tracker=self._job_tracker,
            message_repository=self._message_repository,
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
    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        self._instantiate_declarative_stream(
            BulkParentStreamStreamSlicer(
                super(BulkSalesforceSubStream, self), sync_mode, cursor_field, stream_state, PARENT_SALESFORCE_OBJECTS[self.name]["field"]
            ),
            has_bulk_parent=True,
        )
        yield from self._bulk_job_stream.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)


@BulkSalesforceStream.transformer.registerCustomTransform
def transform_empty_string_to_none(instance: Any, schema: Any):
    """
    BULK API returns a `csv` file, where all values are initially as string type.
    This custom transformer replaces empty lines with `None` value.
    """
    if isinstance(instance, str) and not instance.strip():
        instance = None

    return instance


class IncrementalRestSalesforceStream(RestSalesforceStream, CheckpointMixin, ABC):
    state_checkpoint_interval = 500
    _slice = None

    def __init__(self, replication_key: str, stream_slice_step: str = "P30D", **kwargs):
        self.replication_key = replication_key
        super().__init__(**kwargs)
        self._stream_slice_step = stream_slice_step
        self._stream_slicer_cursor = None
        self._state = {}

    def set_cursor(self, cursor: ConcurrentCursor) -> None:
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

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        self._state = value

    def _get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
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
