#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import json
from abc import abstractmethod
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime

import pendulum
import requests
from typing import Any, List, Mapping, Optional, Tuple, Type, TypeVar, Generic
import freezegun

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import Source, AbstractSource
from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream
from airbyte_cdk.sources.file_based.discovery_policy import AbstractDiscoveryPolicy, DefaultDiscoveryPolicy
from airbyte_cdk.sources.file_based.file_based_source import default_parsers
from airbyte_cdk.sources.file_based.file_based_stream_reader import AbstractFileBasedStreamReader
from airbyte_cdk.sources.file_based.file_types.file_type_parser import FileTypeParser
from airbyte_cdk.sources.file_based.schema_validation_policies import AbstractSchemaValidationPolicy
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from unit_tests.sources.file_based.in_memory_files_source import InMemoryFilesSource


@dataclass
class IncrementalScenarioConfig:
    input_state: List[Mapping[str, Any]] = field(default_factory=list)
    expected_output_state: Optional[Mapping[str, Any]] = None


class TestScenario:
    def __init__(
            self,
            name: str,
            config: Mapping[str, Any],
            expected_check_status: Optional[str],
            expected_catalog: Optional[Mapping[str, Any]],
            expected_logs: List[Mapping[str, Any]],
            expected_records: List[Mapping[str, Any]],
            expected_check_error: Tuple[Optional[Type[Exception]], Optional[str]],
            expected_discover_error: Tuple[Optional[Type[Exception]], Optional[str]],
            expected_read_error: Tuple[Optional[Type[Exception]], Optional[str]],
            incremental_scenario_config: Optional[IncrementalScenarioConfig],
            source: Source,
    ):
        self.name = name
        self.config = config
        self.expected_check_status = expected_check_status
        self.expected_catalog = expected_catalog
        self.expected_logs = expected_logs
        self.expected_records = expected_records
        self.expected_check_error = expected_check_error
        self.expected_discover_error = expected_discover_error
        self.expected_read_error = expected_read_error
        self.source = source
        self.incremental_scenario_config = incremental_scenario_config
        self.validate()

    def validate(self) -> None:
        assert self.name
        if not self.expected_catalog:
            return
        streams = {s["name"] for s in self.config["streams"]} # FIXME I think this should come from the source.streams()
        expected_streams = {s["name"] for s in self.expected_catalog["streams"]}
        #FIXME
        #assert expected_streams <= streams

    def configured_catalog(self, sync_mode: SyncMode) -> Optional[Mapping[str, Any]]:
        if not self.expected_catalog:
            return None
        catalog: Mapping[str, Any] = {"streams": []}
        # FIXME: there should be an input catalog in addition to the expected catalog.
        for stream in self.expected_catalog["streams"]:
            catalog["streams"].append(
                {
                    "stream": stream,
                    "sync_mode": sync_mode.value,
                    "destination_sync_mode": "append",
                }
            )

        return {
            "streams": [
                {
                    "stream": {
                        "name": "accounts",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "events",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "disputes",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "early_fraud_warnings",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "transfers",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "promotion_codes",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "subscriptions",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "subscription_items",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "subscription_schedule",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "setup_intents",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "reviews",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "refunds",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "products",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "invoices",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "plans",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "payouts",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "payment_methods",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "payment_intents",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "invoice_items",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "invoice_line_items",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "customers",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "application_fees_refunds",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "application_fees",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "authorizations",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "balance_transactions",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "bank_accounts",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "cards",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "cardholders",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "external_account_cards",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "external_account_bank_accounts",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "charges",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "checkout_sessions",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["expires_at"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["expires_at"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "checkout_sessions_line_items",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["checkout_session_expires_at"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["checkout_session_expires_at"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "coupons",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "customer_balance_transactions",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "files",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "file_links",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "top_ups",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "setup_attempts",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "usage_records",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                },
                {
                    "stream": {
                        "name": "transfer_reversals",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite",
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "transactions",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh", "incremental"],
                        "source_defined_cursor": True,
                        "default_cursor_field": ["created"],
                        "source_defined_primary_key": [["id"]]
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                    "cursor_field": ["created"],
                    "primary_key": [["id"]]
                },
                {
                    "stream": {
                        "name": "credit_notes",
                        "json_schema": {},
                        "supported_sync_modes": ["full_refresh"]
                    },
                    "sync_mode": "full_refresh",
                    "destination_sync_mode": "overwrite"
                }
            ]
        }


        return catalog

    def input_state(self) -> List[Mapping[str, Any]]:
        if self.incremental_scenario_config:
            return self.incremental_scenario_config.input_state
        else:
            return []

SourceType = TypeVar('SourceType', bound=Source)

class SourceBuilder(Generic[SourceType]):
    @abstractmethod
    def build(self, configured_catalog) -> SourceType:
        ...

SourceBuilderType = TypeVar('SourceBuilderType', bound=SourceBuilder)
class SourceProvider(Generic[SourceType]):
    def __init__(self, owner, source: SourceType):
        self._owner = owner
        self._source = source
    def build(self, configured_catalog) -> SourceType:
        return self._source

@dataclass(eq=True, frozen=True)
class RequestDescriptor:
    url: str
    headers: Optional[Mapping[str, str]]
    body: Optional[Mapping[str, Any]]


@dataclass(eq=True, frozen=True)
class ResponseDescriptor:
    status_code: int
    body: Any # FIXME obviously this is not the right type
    headers: Any


class MockedHttpRequestsSourceBuilder(SourceBuilder[AbstractSource]):

    def __init__(self, owner, source: AbstractSource):
        self._owner = owner
        self._source = source
        self._now = None
        self._request_response_mapping: Mapping[RequestDescriptor, ResponseDescriptor] = {}

    def set_request_response_mapping(self, request_response_mapping: Mapping[str, Any]) -> "MockedHttpRequestsSourceBuilder":
        self._request_response_mapping = request_response_mapping
        return self._owner

    def set_now(self, now):
        self._now = now
        return self._owner

    def build(self, configured_catalog) -> SourceType:

        old_streams = self._source.streams

        if self._now:
            # FIXME: we need a way to scope the freezetime
            print(f"self.now: {self._now}")
            freezegun.freeze_time(self._now).start()

        # FIXME: We want to assert a request is sent X time so we probably want a Mapping[req, List[Optiona[Response]]]
        # and remove the responses from the list as we get them
        request_response_mapping = {RequestDescriptor(url=req.url, headers=None, body=None):
                                        ResponseDescriptor(status_code=res.status_code, body=res.body, headers=None)
                                    for req, res in self._request_response_mapping.items()}

        def mock_http_request(self, request: requests.PreparedRequest, **request_kwargs) -> requests.Response:
            request_headers = dict(request.headers)
            request_headers["Stripe-Account"] = "acct_1JwnoiEcXtiJtvvh"
            request_headers["Authorization"] = "Bearer ****"
            request_headers = dict(request_headers)
            request_body = None
            request_descriptor = RequestDescriptor(url=request.url, headers=None, body=None)
            if request_descriptor not in request_response_mapping:
                raise Exception(f"Unexpected request {request_descriptor}\nExpected one of {request_response_mapping.keys()}")
            else:
                response_descriptor = request_response_mapping[request_descriptor]
                response = requests.Response()
                response.status_code = response_descriptor.status_code
                response._content = json.dumps(json.loads(response_descriptor.body)).encode()
                response.headers["Content-Type"] = "application/json"
                return response

        def streams(self, config: Mapping[str, Any]) -> List[Stream]:
            streams = old_streams(config)
            HttpStream._actually_send_request = mock_http_request
            for stream in streams:
                if isinstance(stream, HttpStream):
                    stream._actually_send_request = mock_http_request.__get__(stream, HttpStream)
                    if hasattr(stream, "parent"):
                        stream.parent._actually_send_request = mock_http_request.__get__(stream.parent, HttpStream)
                elif isinstance(stream, DeclarativeStream):
                    stream.retriever._actually_send_request = mock_http_request.__get__(stream, HttpStream)
                else:
                    raise ValueError(f"Unexpected stream type {stream}")
            return streams

        self._source.streams = streams.__get__(self._source, AbstractSource)

        return self._source

def freeze(obj):
    if isinstance(obj, Mapping):
        return frozenset((key, freeze(value)) for key, value in obj.items())
    elif isinstance(obj, list):
        return tuple(freeze(value) for value in obj)
    else:
        return obj


class FileBasedSourceBuilder(SourceBuilder[InMemoryFilesSource]):
    def __init__(self, owner):
        self._file_write_options: Mapping[str, Any] = {}
        self._parsers = default_parsers
        self._files: Mapping[str, Any] = {}
        self._file_type: Optional[str] = None
        self._availability_strategy: Optional[AvailabilityStrategy] = None
        self._discovery_policy: AbstractDiscoveryPolicy = DefaultDiscoveryPolicy()
        self._validation_policies: Optional[Mapping[str, AbstractSchemaValidationPolicy]] = None
        self._stream_reader: Optional[AbstractFileBasedStreamReader] = None
        self._owner = owner

    def set_files(self, files: Mapping[str, Any]) -> "FileBasedSourceBuilder":
        self._files = files
        return self._owner

    def set_file_type(self, file_type: str) -> "FileBasedSourceBuilder":
        self._file_type = file_type
        return self._owner

    def set_parsers(self, parsers: Mapping[str, FileTypeParser]) -> "FileBasedSourceBuilder":
        self._parsers = parsers
        return self._owner

    def set_availability_strategy(self, availability_strategy: AvailabilityStrategy) -> "FileBasedSourceBuilder":
        self._availability_strategy = availability_strategy
        return self._owner

    def set_discovery_policy(self, discovery_policy: AbstractDiscoveryPolicy) -> "FileBasedSourceBuilder":
        self._discovery_policy = discovery_policy
        return self._owner

    def set_validation_policies(self, validation_policies: Mapping[str, AbstractSchemaValidationPolicy]) -> "FileBasedSourceBuilder":
        self._validation_policies = validation_policies
        return self._owner

    def set_stream_reader(self, stream_reader: AbstractFileBasedStreamReader) -> "FileBasedSourceBuilder":
        self._stream_reader = stream_reader
        return self._owner

    def set_file_write_options(self, file_write_options: Mapping[str, Any]) -> "FileBasedSourceBuilder":
        self._file_write_options = file_write_options
        return self._owner

    def build(self, configured_catalog) -> Source:
        if self._file_type is None:
            raise ValueError("file_type is not set")
        return InMemoryFilesSource(
            self._files,
            self._file_type,
            self._availability_strategy,
            self._discovery_policy,
            self._validation_policies or {},
            self._parsers,
            self._stream_reader,
            configured_catalog,
            self._file_write_options,
            )



class TestScenarioBuilder(Generic[SourceBuilderType, SourceType]):
    def __init__(self, builder_factory = lambda scenario_builder: FileBasedSourceBuilder(scenario_builder)):
        self._name = ""
        self._config: Mapping[str, Any] = {}
        self._expected_check_status: Optional[str] = None
        self._expected_catalog: Mapping[str, Any] = {}
        self._expected_logs: List[Mapping[str, Any]] = []
        self._expected_records: List[Mapping[str, Any]] = []
        self._expected_check_error: Tuple[Optional[Type[Exception]], Optional[str]] = None, None
        self._expected_discover_error: Tuple[Optional[Type[Exception]], Optional[str]] = None, None
        self._expected_read_error: Tuple[Optional[Type[Exception]], Optional[str]] = None, None
        self._incremental_scenario_config: Optional[IncrementalScenarioConfig] = None
        self.source_builder = builder_factory(self)

    def set_name(self, name: str) -> "TestScenarioBuilder":
        self._name = name
        return self

    def set_config(self, config: Mapping[str, Any]) -> "TestScenarioBuilder":
        self._config = config
        return self


    def set_expected_check_status(self, expected_check_status: str) -> "TestScenarioBuilder":
        self._expected_check_status = expected_check_status
        return self

    def set_expected_catalog(self, expected_catalog: Mapping[str, Any]) -> "TestScenarioBuilder":
        self._expected_catalog = expected_catalog
        return self

    def set_expected_logs(self, expected_logs: List[Mapping[str, Any]]) -> "TestScenarioBuilder":
        self._expected_logs = expected_logs
        return self

    def set_expected_records(self, expected_records: List[Mapping[str, Any]]) -> "TestScenarioBuilder":
        self._expected_records = expected_records
        return self


    def set_incremental_scenario_config(self, incremental_scenario_config: IncrementalScenarioConfig) -> "TestScenarioBuilder":
        self._incremental_scenario_config = incremental_scenario_config
        return self

    def set_expected_check_error(self, error: Optional[Type[Exception]], message: str) -> "TestScenarioBuilder":
        self._expected_check_error = error, message
        return self

    def set_expected_discover_error(self, error: Type[Exception], message: str) -> "TestScenarioBuilder":
        self._expected_discover_error = error, message
        return self

    def set_expected_read_error(self, error: Type[Exception], message: str) -> "TestScenarioBuilder":
        self._expected_read_error = error, message
        return self

    def copy(self) -> "TestScenarioBuilder":
        return deepcopy(self)

    def build(self) -> TestScenario:
        return TestScenario(
            self._name,
            self._config,
            self._expected_check_status,
            self._expected_catalog,
            self._expected_logs,
            self._expected_records,
            self._expected_check_error,
            self._expected_discover_error,
            self._expected_read_error,
            self._incremental_scenario_config,
            self.source_builder.build(self.configured_catalog(self._expected_catalog, SyncMode.incremental if self._incremental_scenario_config else SyncMode.full_refresh)),
        )

    def configured_catalog(self, catalog, sync_mode: SyncMode) -> Optional[Mapping[str, Any]]:

        if not self._expected_catalog:
            return None
        configured: Mapping[str, Any] = {"streams": []}
        for stream in self._expected_catalog["streams"]:
            configured["streams"].append(
                {
                    "stream": stream,
                    "sync_mode": sync_mode.value,
                    "destination_sync_mode": "append",
                }
            )

        return configured

