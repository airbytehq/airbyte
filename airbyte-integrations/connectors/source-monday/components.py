#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import logging
import threading
from dataclasses import InitVar, dataclass, field
from datetime import datetime, timedelta
from functools import partial
from typing import Any, ClassVar, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Type, Union

import dpath
import requests

from airbyte_cdk.models import FailureType, SyncMode
from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.auth.oauth import DeclarativeSingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.declarative.decoders.decoder import Decoder
from airbyte_cdk.sources.declarative.decoders.json_decoder import JsonDecoder
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.interpolation import InterpolatedString
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.migrations.state_migration import StateMigration
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.requesters.paginators.strategies.page_increment import PageIncrement
from airbyte_cdk.sources.declarative.schema.inline_schema_loader import InlineSchemaLoader
from airbyte_cdk.sources.declarative.transformations import RecordTransformation
from airbyte_cdk.sources.declarative.types import Config, StreamSlice, StreamState
from airbyte_cdk.sources.types import Record
from airbyte_cdk.utils.airbyte_secrets_utils import add_to_secrets
from airbyte_cdk.utils.datetime_helpers import ab_datetime_now
from airbyte_cdk.utils.traced_exception import AirbyteTracedException


logger = logging.getLogger("airbyte")


@dataclass
class MondayOAuthAuthenticator(DeclarativeAuthenticator):
    """
    OAuth 2.1 authenticator that first migrates legacy OAuth credentials.

    Sources authorized before connector 3.0.0 hold a non-expiring legacy access token and no refresh token. Monday
    exposes a one-time, temporary migration endpoint that exchanges such a token for an OAuth 2.1 access/refresh
    token pair without user consent (https://developer.monday.com/apps/docs/migrating-to-the-new-oauth-flow#6-migrate-legacy-api-tokens).
    When the config has no refresh token, the migration is attempted once, the resulting pair is persisted through
    a config control message, and the request is then delegated to the regular refresh-token authenticator. Any
    migration failure surfaces as a config error asking the user to re-authenticate.
    """

    config: Mapping[str, Any]
    oauth: DeclarativeSingleUseRefreshTokenOauth2Authenticator
    migration_endpoint: str = "https://auth.monday.com/oauth_ms/oauth/migrate"

    REAUTHENTICATE_MESSAGE = (
        "This Monday source was authorized with Monday's legacy OAuth flow and its credentials could not be migrated "
        "automatically to the new OAuth flow. Re-authenticate this source in its settings to continue syncing."
    )
    _migration_lock: ClassVar[threading.Lock] = threading.Lock()

    @property
    def auth_header(self) -> str:
        return "Authorization"

    @property
    def token(self) -> str:
        self._migrate_legacy_token_if_needed()
        return f"Bearer {self.oauth.get_access_token()}"

    def get_auth_header(self) -> Mapping[str, Any]:
        self._migrate_legacy_token_if_needed()
        return self.oauth.get_auth_header()

    def _migrate_legacy_token_if_needed(self) -> None:
        if self.oauth.get_refresh_token():
            return
        with self._migration_lock:
            if self.oauth.get_refresh_token():
                return
            access_token, refresh_token, expires_in = self._migrate_legacy_token()
            add_to_secrets(access_token)
            add_to_secrets(refresh_token)
            self.oauth.access_token = access_token
            self.oauth.set_refresh_token(refresh_token)
            self.oauth.set_token_expiry_date(ab_datetime_now() + timedelta(seconds=expires_in))
            self.oauth._emit_control_message()
            logger.info("Migrated legacy Monday OAuth credentials to the new OAuth flow.")

    def _migrate_legacy_token(self) -> tuple[str, str, int]:
        credentials = self.config.get("credentials", {})
        legacy_access_token = credentials.get("access_token")
        if not legacy_access_token:
            raise AirbyteTracedException(
                internal_message="OAuth credentials have neither an access token nor a refresh token.",
                message=self.REAUTHENTICATE_MESSAGE,
                failure_type=FailureType.config_error,
            )
        try:
            response = requests.post(
                self.migration_endpoint,
                json={
                    "api_token": legacy_access_token,
                    "client_id": credentials.get("client_id"),
                    "client_secret": credentials.get("client_secret"),
                },
                headers={"Content-Type": "application/json"},
            )
        except requests.exceptions.RequestException as exception:
            raise AirbyteTracedException(
                internal_message=f"Legacy Monday OAuth token migration request failed: {exception}",
                message="Could not reach Monday's OAuth migration endpoint. The sync will be retried.",
                failure_type=FailureType.transient_error,
                exception=exception,
            ) from exception

        if response.status_code == 429 or response.status_code >= 500:
            raise AirbyteTracedException(
                internal_message=f"Legacy Monday OAuth token migration returned HTTP {response.status_code}: {response.text}",
                message="Monday's OAuth migration endpoint is rate limited or unavailable. The sync will be retried.",
                failure_type=FailureType.transient_error,
            )

        body = self._parse_json_body(response)
        access_token, refresh_token = body.get("access_token"), body.get("refresh_token")
        if not response.ok or not access_token or not refresh_token:
            provider_error = body.get("error_description") or body.get("error") or body.get("message") or response.text
            raise AirbyteTracedException(
                internal_message=f"Legacy Monday OAuth token migration rejected with HTTP {response.status_code}: {provider_error}",
                message=f"{self.REAUTHENTICATE_MESSAGE} Monday responded: {provider_error}",
                failure_type=FailureType.config_error,
            )
        return access_token, refresh_token, int(body.get("expires_in") or 3600)

    @staticmethod
    def _parse_json_body(response: requests.Response) -> Mapping[str, Any]:
        try:
            body = response.json()
        except ValueError:
            return {}
        return body if isinstance(body, Mapping) else {}


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
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        response_body_generator = self.decoder.decode(response)
        for response_body in response_body_generator:
            if not response_body["data"]["boards"]:
                continue

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

                    yield new_record


@dataclass
class MondayIncrementalItemsExtractor(RecordExtractor):
    """
    Record extractor that searches a decoded response over a path defined as an array of fields.
    """

    field_path: List[Union[InterpolatedString, str]]
    config: Config
    parameters: InitVar[Mapping[str, Any]]
    field_path_pagination: List[Union[InterpolatedString, str]] = field(default_factory=list)
    decoder: Decoder = field(default_factory=lambda: JsonDecoder(parameters={}))

    def __post_init__(self, parameters: Mapping[str, Any]):
        # Convert string paths to InterpolatedString for both field_path and field_path_pagination
        self._field_path = [InterpolatedString.create(p, parameters=parameters) if isinstance(p, str) else p for p in self.field_path]
        self._field_path_pagination = [
            InterpolatedString.create(p, parameters=parameters) if isinstance(p, str) else p for p in self.field_path_pagination
        ]

    def _try_extract_records(
        self, response: requests.Response, field_path: List[Union[InterpolatedString, str]]
    ) -> Iterable[Mapping[str, Any]]:
        for body in self.decoder.decode(response):
            if len(field_path) == 0:
                extracted = body
            else:
                path = [p.eval(self.config) for p in field_path]
                if "*" in path:
                    extracted = dpath.values(body, path)
                else:
                    extracted = dpath.get(body, path, default=[])

            if extracted:
                if isinstance(extracted, list) and None in extracted:
                    logger.warning(f"Record with null value received; errors: {body.get('errors')}")
                    yield from (x for x in extracted if x)
                else:
                    yield from extracted if isinstance(extracted, list) else [extracted]

    def extract_records(self, response: requests.Response) -> Iterable[Mapping[str, Any]]:
        # Try primary field path
        has_records = False
        for record in self._try_extract_records(response, self._field_path):
            has_records = True
            yield record

        # Fallback to pagination path if no records and path exists
        if not has_records and self._field_path_pagination:
            yield from self._try_extract_records(response, self._field_path_pagination)


@dataclass(kw_only=True)
class MondayGraphqlRequester(HttpRequester):
    NEXT_PAGE_TOKEN_FIELD_NAME = "next_page_token"

    schema_loader: InlineSchemaLoader
    limit: Union[InterpolatedString, str, int] = None
    nested_limit: Union[InterpolatedString, str, int] = None

    def __post_init__(self, parameters: Mapping[str, Any]):
        super(MondayGraphqlRequester, self).__post_init__(parameters)
        self.limit = InterpolatedString.create(self.limit, parameters=parameters)
        self.nested_limit = InterpolatedString.create(self.nested_limit, parameters=parameters)
        self.name = parameters.get("name", "").lower()
        self.stream_sync_mode = (
            SyncMode.full_refresh if parameters.get("stream_sync_mode", "full_refresh") == "full_refresh" else SyncMode.incremental
        )

    def _ensure_type(self, t: Type, o: Any):
        """
        Ensure given object `o` is of type `t`
        """
        if not isinstance(o, t):
            raise TypeError(f"{type(o)} {o} is not of type {t}")

    def _get_schema_root_properties(self):
        schema = self.schema_loader.get_json_schema()[self.name]["properties"]

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

        # when querying the boards stream (object_name == "boards"), filter by board_ids if they provided in the config
        if object_name == "boards" and "board_ids" in self.config:
            # if we are building a query for incremental syncs, board ids are already present under 'ids' key in object_arguments (as a result of fetching the activity_logs stream first)
            # These ids are already an intersection of the board_ids provided in the config and the ones that must be fetched for the incremental sync and need not be overridden
            if "ids" not in object_arguments:
                object_arguments["ids"] = self.config.get("board_ids")

        arguments = self._get_object_arguments(**object_arguments)
        arguments = f"({arguments})" if arguments else ""

        if object_name == "column_values":
            fields.remove("display_value")
            if "linked_item_ids" in fields:
                fields.remove("linked_item_ids")
            fields.extend(
                [
                    "... on MirrorValue{display_value}",
                    "... on BoardRelationValue{display_value,linked_item_ids}",
                    "... on DependencyValue{display_value,linked_item_ids}",
                ]
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
            # since items are a subresource of boards, when querying items, filter by board_ids if provided in the config
            if "board_ids" in self.config and "ids" not in object_arguments:
                object_arguments["ids"] = self.config.get("board_ids")
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
            if not arguments:
                # when providing empty arguments in () API returns error
                return f"{object_name}{query}"
            return f"{object_name}({arguments}){query}"
        return self._build_query(object_name=object_name, field_schema=field_schema, **object_arguments)

    def _build_activity_query(self, object_name: str, field_schema: dict, sub_page: Optional[int], **object_arguments) -> str:
        """
        Special optimization needed for items stream. Starting October 3rd, 2022 items can only be reached through boards.
        See https://developer.monday.com/api-reference/docs/items-queries#items-queries
        """
        nested_limit = self.nested_limit.eval(self.config)

        created_at = (object_arguments.get("stream_slice", dict()) or dict()).get("start_time")
        if "stream_slice" in object_arguments:
            object_arguments.pop("stream_slice")

        # 1 is default start time, so we can skip it to get all the data
        if created_at == "1":
            created_at = None
        else:
            created_at = datetime.fromtimestamp(int(created_at)).strftime("%Y-%m-%dT%H:%M:%SZ")

        query = self._build_query(object_name, field_schema, limit=nested_limit, page=sub_page, fromt=created_at)
        if "board_ids" in self.config and "ids" not in object_arguments:
            object_arguments["ids"] = self.config.get("board_ids")
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
        headers["API-Version"] = "2026-01"
        return headers

    def get_request_body_json(  # type: ignore
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Optional[Mapping[str, Any]]:
        """
        Combines queries to a single GraphQL query.
        """
        limit = self.limit.eval(self.config)

        page = next_page_token and next_page_token[self.NEXT_PAGE_TOKEN_FIELD_NAME]
        if self.name == "boards" and stream_slice:
            if self.stream_sync_mode == SyncMode.full_refresh:
                # incremental sync parameters are not needed for full refresh
                stream_slice = {}
            else:
                stream_slice = {"ids": stream_slice.get("ids")}
            query_builder = partial(self._build_query, **stream_slice)
        elif self.name == "items":
            # `items` stream use a separate pagination strategy where first level pages are across `boards` and sub-pages are across `items`
            page, sub_page = page if page else (None, None)
            if self.stream_sync_mode == SyncMode.full_refresh:
                query_builder = partial(self._build_items_query, sub_page=sub_page)
            else:
                query_builder = partial(self._build_items_incremental_query, stream_slice=stream_slice)
        elif self.name == "teams":
            query_builder = self._build_teams_query
        elif self.name == "activity_logs":
            page, sub_page = page if page else (None, None)
            query_builder = partial(self._build_activity_query, sub_page=sub_page, stream_slice=stream_slice)
        else:
            query_builder = self._build_query
        query = query_builder(
            object_name=self.name,
            field_schema=self._get_schema_root_properties(),
            limit=limit or None,
            page=page,
        )
        return {"query": f"{{{query}}}"}

    # We are using an LRU cache in should_retry() method which requires all incoming arguments (including self) to be hashable.
    # Dataclasses by default are not hashable, so we need to define __hash__(). Alternatively, we can set @dataclass(frozen=True),
    # but this has a cascading effect where all dataclass fields must also be set to frozen.
    def __hash__(self):
        return hash(tuple(self.__dict__))


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

    def next_page_token(
        self, response: requests.Response, last_page_size: int, last_record: Optional[Record], last_page_token_value: Optional[Any]
    ) -> Optional[Tuple[Optional[int], Optional[int]]]:
        """
        Determines page and subpage numbers for the `items` stream

        Attributes:
            response: Contains `boards` and corresponding lists of `items` for each `board`
            last_records: Parsed `items` from the response
        """
        if last_page_size >= self.page_size:
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

    def next_page_token(
        self, response: requests.Response, last_page_size: int, last_record: Optional[Record], last_page_token_value: Optional[Any]
    ) -> Optional[Tuple[Optional[int], Optional[int]]]:
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


class MondayStateMigration(StateMigration):
    def migrate(self, stream_state: Mapping[str, Any]) -> Mapping[str, Any]:
        del stream_state["activity_logs"]
        return stream_state

    def should_migrate(self, stream_state: Mapping[str, Any]) -> bool:
        return "activity_logs" in stream_state


@dataclass
class MondayTransformation(RecordTransformation):
    def transform(self, record: MutableMapping[str, Any], config: Optional[Config] = None, **kwargs) -> MutableMapping[str, Any]:
        # Oncall issue: https://github.com/airbytehq/oncall/issues/4337
        column_values = record.get("column_values", [])
        for values in column_values:
            display_value, text = values.get("display_value"), values.get("text")
            if display_value and not text:
                values["text"] = display_value

        return record
