#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
from dataclasses import InitVar, dataclass, field
from datetime import datetime
from functools import partial
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type, Union

import dpath
import requests

from airbyte_cdk.models import AirbyteMessage, SyncMode, Type
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.incremental import DeclarativeCursor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.partition_routers.substream_partition_router import ParentStreamConfig
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement
from airbyte_cdk.sources.declarative.requesters.request_option import RequestOptionType
from airbyte_cdk.sources.declarative.schema.json_file_schema_loader import JsonFileSchemaLoader
from airbyte_cdk.sources.declarative.types import Config, Record, StreamSlice, StreamState
from airbyte_cdk.sources.streams.core import Stream


RequestInput = Union[str, Mapping[str, str]]
logger = logging.getLogger("airbyte")


class ItemPaginationStrategy(PageIncrement):
    """
    Page increment strategy with subpages for the `items` stream.

    From the `items` documentation https://developer.monday.com/api-reference/docs/items:
        Please note that you cannot return more than 100 items per query when using items at the root.
        To adjust your query, try only returning items on a specific board, nesting items inside a boards query,
        looping through the boards on your account, or querying less than 100 items at a time.

    This pagination strategy supports nested loop through `boards` on the top level and `items` on the second.
    See boards documentation for more details: https://developer.monday.com/api-reference/docs/boards#queries.
    """

    def __post_init__(self, parameters: Mapping[str, Any]):
        # `self._page` corresponds to board page number
        # `self._sub_page` corresponds to item page number within its board
        self.start_from_page = 1
        self._page: Optional[int] = self.start_from_page
        self._sub_page: Optional[int] = self.start_from_page

    def next_page_token(self, response, last_records: List[Mapping[str, Any]]) -> Optional[Tuple[Optional[int], Optional[int]]]:
        """
        Determines page and subpage numbers for the `items` stream

        Attributes:
            response: Contains `boards` and corresponding lists of `items` for each `board`
            last_records: Parsed `items` from the response
        """
        if len(last_records) >= self.page_size:
            self._sub_page += 1
        else:
            self._sub_page = self.start_from_page
            if response.json()["data"].get("boards"):
                self._page += 1
            else:
                return None

        return self._page, self._sub_page


class ItemCursorPaginationStrategy(PageIncrement):
    """
    Page increment strategy with subpages for the `items` stream.

    From the `items` documentation https://developer.monday.com/api-reference/docs/items:
        Please note that you cannot return more than 100 items per query when using items at the root.
        To adjust your query, try only returning items on a specific board, nesting items inside a boards query,
        looping through the boards on your account, or querying less than 100 items at a time.

    This pagination strategy supports nested loop through `boards` on the top level and `items` on the second.
    See boards documentation for more details: https://developer.monday.com/api-reference/docs/boards#queries.
    """

    def __post_init__(self, parameters: Mapping[str, Any]):
        # `self._page` corresponds to board page number
        # `self._sub_page` corresponds to item page number within its board
        self.start_from_page = 1
        self._page: Optional[int] = self.start_from_page
        self._sub_page: Optional[int] = self.start_from_page

    def next_page_token(self, response, last_records: List[Mapping[str, Any]]) -> Optional[Tuple[Optional[int], Optional[int]]]:
        """
        `items` stream use a separate 2 level pagination strategy where:
        1st level `boards` - incremental pagination
        2nd level `items_page` - cursor pagination

        Attributes:
            response: Contains `boards` and corresponding lists of `items` for each `board`
            last_records: Parsed `items` from the response
        """
        data = response.json()["data"]
        boards = data.get("boards", [])
        next_items_page = data.get("next_items_page", {})
        if boards:
            # there is always only one board due to limit=1, so in one request we extract all 'items_page' for one board only
            board = boards[0]
            cursor = board.get("items_page", {}).get("cursor", None)
        elif next_items_page:
            cursor = next_items_page.get("cursor", None)
        else:
            # Finish pagination if there is no more data
            return None

        if cursor:
            return self._page, cursor
        else:
            self._page += 1
            return self._page, None


@dataclass
class MondayGraphqlRequester(HttpRequester):
    NEXT_PAGE_TOKEN_FIELD_NAME = "next_page_token"

    limit: Union[InterpolatedString, str, int] = None
    nested_limit: Union[InterpolatedString, str, int] = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        super(MondayGraphqlRequester, self).__post_init__(parameters)

        self.limit = InterpolatedString.create(self.limit, parameters=parameters)
        self.nested_limit = InterpolatedString.create(self.nested_limit, parameters=parameters)

    def _ensure_type(self, t: Type, o: Any):
        """
        Ensure given object `o` is of type `t`
        """
        if not isinstance(o, t):
            raise TypeError(f"{type(o)} {o} is not of type {t}")

    def _get_schema_root_properties(self):
        schema_loader = JsonFileSchemaLoader(config=self.config, parameters={"name": self.name})
        schema = schema_loader.get_json_schema()["properties"]

        # delete fields that will be created by extractor
        delete_fields = ["updated_at_int", "created_at_int", "pulse_id"]
        if self.name == "activity_logs":
            delete_fields.append("board_id")
        for field in delete_fields:
            if field in schema:
                schema.pop(field)

        return schema

    def _get_object_arguments(self, **object_arguments) -> str:
        return ",".join(
            [
                f"{argument}:{value}" if argument != "fromt" else f'from:"{value}"'
                for argument, value in object_arguments.items()
                if value is not None
            ]
        )

    def _build_query(self, object_name: str, field_schema: dict, **object_arguments) -> str:
        """
        Recursive function that builds a GraphQL query string by traversing given stream schema properties.
        Attributes
            object_name (str): the name of root object
            field_schema (dict): configured catalog schema for current stream
            object_arguments (dict): arguments such as limit, page, ids, ... etc to be passed for given object
        """
        fields = []
        for field, nested_schema in field_schema.items():
            nested_fields = nested_schema.get("properties", nested_schema.get("items", {}).get("properties"))
            if nested_fields:
                # preconfigured_arguments = get properties from schema or any other source ...
                # fields.append(self._build_query(field, nested_fields, **preconfigured_arguments))
                fields.append(self._build_query(field, nested_fields))
            else:
                fields.append(field)

        arguments = self._get_object_arguments(**object_arguments)
        arguments = f"({arguments})" if arguments else ""

        if object_name == "column_values":
            fields.remove("display_value")
            fields.extend(
                ["... on MirrorValue{display_value}", "... on BoardRelationValue{display_value}", "... on DependencyValue{display_value}"]
            )

        fields = ",".join(fields)

        if object_name in ["items_page", "next_items_page"]:
            query = f"{object_name}{arguments}{{cursor,items{{{fields}}}}}"
        else:
            query = f"{object_name}{arguments}{{{fields}}}"
        return query

    def _build_items_query(self, object_name: str, field_schema: dict, sub_page: Optional[int], **object_arguments) -> str:
        """
        Special optimization needed for items stream. Starting October 3rd, 2022 items can only be reached through boards.
        See https://developer.monday.com/api-reference/docs/items-queries#items-queries

        Comparison of different APIs queries:
        2023-07:
            boards(limit: 1)         {      items(limit: 20)                 {              field1, field2, ...  }}
            boards(limit: 1, page:2) {      items(limit: 20, page:2)         {              field1, field2, ...  }} boards and items paginations
        2024_01:
            boards(limit: 1)         { items_page(limit: 20)                 {cursor, items{field1, field2, ...} }}
            boards(limit: 1, page:2) { items_page(limit: 20)                 {cursor, items{field1, field2, ...} }} - boards pagination
                                  next_items_page(limit: 20, cursor: "blaa") {cursor, items{field1, field2, ...} }  - items pagination

        """
        nested_limit = self.nested_limit.eval(self.config)

        if sub_page:
            query = self._build_query("next_items_page", field_schema, limit=nested_limit, cursor=f'"{sub_page}"')
        else:
            query = self._build_query("items_page", field_schema, limit=nested_limit)
            arguments = self._get_object_arguments(**object_arguments)
            query = f"boards({arguments}){{{query}}}"

        return query

    def _build_items_incremental_query(self, object_name: str, field_schema: dict, stream_slice: dict, **object_arguments) -> str:
        """
        Special optimization needed for items stream. Starting October 3rd, 2022 items can only be reached through boards.
        See https://developer.monday.com/api-reference/docs/items-queries#items-queries
        """
        nested_limit = self.nested_limit.eval(self.config)

        object_arguments["limit"] = nested_limit
        object_arguments["ids"] = stream_slice["ids"]
        return self._build_query("items", field_schema, **object_arguments)

    def _build_teams_query(self, object_name: str, field_schema: dict, **object_arguments) -> str:
        """
        Special optimization needed for tests to pass successfully because of rate limits.
        It makes a query cost less points, but it is never used in production
        """
        teams_limit = self.config.get("teams_limit")
        if teams_limit:
            self._ensure_type(int, teams_limit)
            arguments = self._get_object_arguments(**object_arguments)
            query = f"{{id,name,picture_url,users(limit:{teams_limit}){{id}}}}"
            return f"{object_name}({arguments}){query}"
        return self._build_query(object_name=object_name, field_schema=field_schema, **object_arguments)

    def _build_activity_query(self, object_name: str, field_schema: dict, sub_page: Optional[int], **object_arguments) -> str:
        """
        Special optimization needed for items stream. Starting October 3rd, 2022 items can only be reached through boards.
        See https://developer.monday.com/api-reference/docs/items-queries#items-queries
        """
        nested_limit = self.nested_limit.eval(self.config)

        created_at = (object_arguments.get("stream_state", dict()) or dict()).get("created_at_int")
        object_arguments.pop("stream_state")

        if created_at:
            created_at = datetime.fromtimestamp(created_at).strftime("%Y-%m-%dT%H:%M:%SZ")

        query = self._build_query(object_name, field_schema, limit=nested_limit, page=sub_page, fromt=created_at)
        arguments = self._get_object_arguments(**object_arguments)
        return f"boards({arguments}){{{query}}}"

    def get_request_headers(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        headers = super().get_request_headers(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        headers["API-Version"] = "2024-01"
        return headers

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> MutableMapping[str, Any]:
        """
        Combines queries to a single GraphQL query.
        """
        limit = self.limit

        page = next_page_token and next_page_token[self.NEXT_PAGE_TOKEN_FIELD_NAME]
        if self.name == "boards" and stream_slice:
            query_builder = partial(self._build_query, **stream_slice)
        elif self.name == "items":
            # `items` stream use a separate pagination strategy where first level pages are across `boards` and sub-pages are across `items`
            page, sub_page = page if page else (None, None)
            if not stream_slice:
                query_builder = partial(self._build_items_query, sub_page=sub_page)
            else:
                query_builder = partial(self._build_items_incremental_query, stream_slice=stream_slice)
        elif self.name == "teams":
            query_builder = self._build_teams_query
        elif self.name == "activity_logs":
            page, sub_page = page if page else (None, None)
            query_builder = partial(self._build_activity_query, sub_page=sub_page, stream_state=stream_state)
        else:
            query_builder = self._build_query
        query = query_builder(
            object_name=self.name,
            field_schema=self._get_schema_root_properties(),
            limit=limit or None,
            page=page,
        )
        return {"query": f"query{{{query}}}"}

    # We are using an LRU cache in should_retry() method which requires all incoming arguments (including self) to be hashable.
    # Dataclasses by default are not hashable, so we need to define __hash__(). Alternatively, we can set @dataclass(frozen=True),
    # but this has a cascading effect where all dataclass fields must also be set to frozen.
    def __hash__(self):
        return hash(tuple(self.__dict__))


@dataclass
class MondayActivityExtractor(RecordExtractor):
    """
    Record extractor that extracts record of the form from activity logs stream:

    { "list": { "ID_1": record_1, "ID_2": record_2, ... } }

    Attributes:
        parameters (Mapping[str, Any]): Additional runtime parameters to be used for string interpolation
        decoder (Decoder): The decoder responsible to transfom the response in a Mapping
    """

    parameters: InitVar[Mapping[str, Any]]
    decoder: Decoder = JsonDecoder(parameters={})

    def extract_records(self, response: requests.Response) -> List[Record]:
        response_body = self.decoder.decode(response)
        result = []
        if not response_body["data"]["boards"]:
            return result

        for board_data in response_body["data"]["boards"]:
            if not isinstance(board_data, dict) or not board_data.get("activity_logs"):
                continue
            for record in board_data.get("activity_logs", []):
                json_data = json.loads(record["data"])
                new_record = record
                if record.get("created_at"):
                    new_record.update({"created_at_int": int(record.get("created_at", 0)) // 10_000_000})
                else:
                    continue

                if record.get("entity") == "pulse" and json_data.get("pulse_id"):
                    new_record.update({"pulse_id": json_data.get("pulse_id")})

                if record.get("entity") == "board" and json_data.get("board_id"):
                    new_record.update({"board_id": json_data.get("board_id")})

                result.append(new_record)

        return result


@dataclass
class MondayIncrementalItemsExtractor(RecordExtractor):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.
    """

    field_path: List[Union[InterpolatedString, str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    field_path_pagination: List[Union[InterpolatedString, str]] = field(default_factory=list)
    field_path_incremental: List[Union[InterpolatedString, str]] = field(default_factory=list)
    decoder: Decoder = JsonDecoder(parameters={})

    def __post_init__(self, parameters: Mapping[str, Any]):
        for field_list in (self.field_path, self.field_path_pagination, self.field_path_incremental):
            for path_index in range(len(field_list)):
                if isinstance(field_list[path_index], str):
                    field_list[path_index] = InterpolatedString.create(field_list[path_index], parameters=parameters)

    def try_extract_records(self, response: requests.Response, field_path: List[Union[InterpolatedString, str]]) -> List[Record]:
        response_body = self.decoder.decode(response)

        path = [path.eval(self.config) for path in field_path]
        extracted = dpath.values(response_body, path) if path else response_body

        pattern_path = "*" in path
        if not pattern_path:
            extracted = dpath.get(response_body, path, default=[])

        if extracted:
            if isinstance(extracted, list) and None in extracted:
                logger.warning(f"Record with null value received; errors: {response_body.get('errors')}")
                return [x for x in extracted if x]
            return extracted if isinstance(extracted, list) else [extracted]
        return []

    def extract_records(self, response: requests.Response) -> List[Record]:
        result = self.try_extract_records(response, field_path=self.field_path)
        if not result and self.field_path_pagination:
            result = self.try_extract_records(response, self.field_path_pagination)
        if not result and self.field_path_incremental:
            result = self.try_extract_records(response, self.field_path_incremental)

        for record in result:
            if "updated_at" in record:
                record["updated_at_int"] = int(datetime.strptime(record["updated_at"], "%Y-%m-%dT%H:%M:%S%z").timestamp())

            column_values = record.get("column_values", [])
            for values in column_values:
                display_value, text = values.get("display_value"), values.get("text")
                if display_value and not text:
                    values["text"] = display_value

        return result


@dataclass
class IncrementalSingleSlice(DeclarativeCursor):
    cursor_field: Union[InterpolatedString, str]
    config: Config
    parameters: InitVar[Mapping[str, Any]]

    def __post_init__(self, parameters: Mapping[str, Any]):
        self._state = {}
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)

    def get_request_params(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.request_parameter, stream_slice)

    def get_request_headers(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.header, stream_slice)

    def get_request_body_data(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_data, stream_slice)

    def get_request_body_json(
        self,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping]:
        # Pass the stream_slice from the argument, not the cursor because the cursor is updated after processing the response
        return self._get_request_option(RequestOptionType.body_json, stream_slice)

    def _get_request_option(self, option_type: RequestOptionType, stream_slice: StreamSlice):
        return {}

    def get_stream_state(self) -> StreamState:
        return self._state

    def set_initial_state(self, stream_state: StreamState):
        cursor_value = stream_state.get(self.cursor_field.eval(self.config))
        if cursor_value:
            self._state[self.cursor_field.eval(self.config)] = cursor_value

    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        latest_record = self._state if self.is_greater_than_or_equal(self._state, most_recent_record) else most_recent_record

        if not latest_record:
            return
        self._state[self.cursor_field.eval(self.config)] = latest_record[self.cursor_field.eval(self.config)]

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        yield StreamSlice(partition={}, cursor_slice={})

    def should_be_synced(self, record: Record) -> bool:
        """
        As of 2023-06-28, the expectation is that this method will only be used for semi-incremental and data feed and therefore the
        implementation is irrelevant for greenhouse
        """
        return True

    def is_greater_than_or_equal(self, first: Record, second: Record) -> bool:
        """
        Evaluating which record is greater in terms of cursor. This is used to avoid having to capture all the records to close a slice
        """
        first_cursor_value = first.get(self.cursor_field.eval(self.config)) if first else None
        second_cursor_value = second.get(self.cursor_field.eval(self.config)) if second else None
        if first_cursor_value and second_cursor_value:
            return first_cursor_value > second_cursor_value
        elif first_cursor_value:
            return True
        else:
            return False

    def select_state(self, stream_slice: Optional[StreamSlice] = None) -> Optional[StreamState]:
        return self.get_stream_state()


@dataclass
class IncrementalSubstreamSlicer(IncrementalSingleSlice):
    """
    Like SubstreamSlicer, but works incrementaly with both parent and substream.

    Input Arguments:

    :: cursor_field: srt - substream cursor_field value
    :: parent_complete_fetch: bool - If `True`, all slices is fetched into a list first, then yield.
        If `False`, substream emits records on each parernt slice yield.
    :: parent_stream_configs: ParentStreamConfig - Describes how to create a stream slice from a parent stream.

    """

    config: Config
    parameters: InitVar[Mapping[str, Any]]
    cursor_field: Union[InterpolatedString, str]
    parent_stream_configs: List[ParentStreamConfig]
    nested_items_per_page: int
    parent_complete_fetch: bool = field(default=False)

    def __post_init__(self, parameters: Mapping[str, Any]):
        super().__post_init__(parameters)
        if not self.parent_stream_configs:
            raise ValueError("IncrementalSubstreamSlicer needs at least 1 parent stream")
        self.cursor_field = InterpolatedString.create(self.cursor_field, parameters=parameters)
        # parent stream parts
        self.parent_config: ParentStreamConfig = self.parent_stream_configs[0]
        self.parent_stream: Stream = self.parent_config.stream
        self.parent_stream_name: str = self.parent_stream.name
        self.parent_cursor_field: str = self.parent_stream.cursor_field
        self.parent_sync_mode: SyncMode = SyncMode.incremental if self.parent_stream.supports_incremental is True else SyncMode.full_refresh
        self.substream_slice_field: str = self.parent_stream_configs[0].partition_field.eval(self.config)
        self.parent_field: str = self.parent_stream_configs[0].parent_key.eval(self.config)

    def set_initial_state(self, stream_state: StreamState):
        cursor_value = stream_state.get(self.cursor_field.eval(self.config))
        if cursor_value:
            self._state[self.cursor_field.eval(self.config)] = cursor_value
        if self.parent_stream_name in stream_state and stream_state.get(self.parent_stream_name, {}).get(self.parent_cursor_field):
            self._state[self.parent_stream_name] = {
                self.parent_cursor_field: stream_state[self.parent_stream_name][self.parent_cursor_field]
            }

    def close_slice(self, stream_slice: StreamSlice, most_recent_record: Optional[Record]) -> None:
        latest_record = self._state if self.is_greater_than_or_equal(self._state, most_recent_record) else most_recent_record

        if not latest_record:
            return

        max_state = latest_record[self.cursor_field.eval(self.config)]
        self._state[self.cursor_field.eval(self.config)] = max_state

        if self.parent_stream:
            parent_state = self.parent_stream.state or {self.parent_cursor_field: max_state}
            self._state[self.parent_stream_name] = parent_state

    def read_parent_stream(
        self, sync_mode: SyncMode, cursor_field: Optional[str], stream_state: Mapping[str, Any]
    ) -> Iterable[Mapping[str, Any]]:
        self.parent_stream.state = stream_state

        # check if state is empty ->
        if not stream_state.get(self.parent_cursor_field):
            # yield empty slice for complete fetch of items stream
            yield StreamSlice(partition={}, cursor_slice={})
            return

        all_ids = set()
        slice_ids = list()
        empty_parent_slice = True

        for parent_slice in self.parent_stream.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state):
            for parent_record in self.parent_stream.read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=parent_slice, stream_state=stream_state
            ):
                # Skip non-records (eg AirbyteLogMessage)
                if isinstance(parent_record, AirbyteMessage):
                    if parent_record.type == Type.RECORD:
                        parent_record = parent_record.record.data

                try:
                    substream_slice = dpath.get(parent_record, self.parent_field)
                except KeyError:
                    pass
                else:
                    empty_parent_slice = False

                    # check if record with this id was already processed
                    if substream_slice not in all_ids:
                        all_ids.add(substream_slice)
                        slice_ids.append(substream_slice)

                        # yield slice with desired number of ids
                        if self.nested_items_per_page == len(slice_ids):
                            yield StreamSlice(partition={self.substream_slice_field: slice_ids}, cursor_slice={})
                            slice_ids = list()
        # yield leftover ids if any left
        if slice_ids:
            yield StreamSlice(partition={self.substream_slice_field: slice_ids}, cursor_slice={})

        # If the parent slice contains no records
        if empty_parent_slice:
            yield from []

    def stream_slices(self) -> Iterable[Mapping[str, Any]]:
        parent_state = (self._state or {}).get(self.parent_stream_name, {})

        slices_generator = self.read_parent_stream(self.parent_sync_mode, self.parent_cursor_field, parent_state)
        yield from [slice for slice in slices_generator] if self.parent_complete_fetch else slices_generator
