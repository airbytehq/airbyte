# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import _collections_abc
import hashlib
import json
import logging
import tempfile
from collections import defaultdict
from collections.abc import Iterable, Iterator, MutableMapping
from dataclasses import dataclass, field
from enum import Enum
from functools import cache
from pathlib import Path
from typing import Any, Dict, List, Optional

import dagger
import requests
from airbyte_protocol.models import (
    AirbyteCatalog,  # type: ignore
    AirbyteMessage,  # type: ignore
    AirbyteStateMessage,  # type: ignore
    AirbyteStreamStatusTraceMessage,  # type: ignore
    ConfiguredAirbyteCatalog,  # type: ignore
    TraceType,  # type: ignore
)
from airbyte_protocol.models import Type as AirbyteMessageType
from genson import SchemaBuilder  # type: ignore
from mitmproxy import http
from pydantic import ValidationError

from live_tests.commons.backends import DuckDbBackend, FileBackend
from live_tests.commons.secret_access import get_airbyte_api_key
from live_tests.commons.utils import (
    get_connector_container,
    get_http_flows_from_mitm_dump,
    mitm_http_stream_to_har,
    sanitize_stream_name,
    sort_dict_keys,
)


class UserDict(_collections_abc.MutableMapping):  # type: ignore
    # Start by filling-out the abstract methods
    def __init__(self, _dict: Optional[MutableMapping] = None, **kwargs: Any):
        self.data: MutableMapping = {}
        if _dict is not None:
            self.update(_dict)
        if kwargs:
            self.update(kwargs)

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, key: Any) -> Any:
        if key in self.data:
            return self.data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key: Any, item: Any) -> None:
        self.data[key] = item

    def __delitem__(self, key: Any) -> None:
        del self.data[key]

    def __iter__(self) -> Iterator:
        return iter(self.data)

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key: Any) -> bool:
        return key in self.data

    # Now, add the methods in dicts but not in MutableMapping
    def __repr__(self) -> str:
        return repr(self.data)

    def __or__(self, other: UserDict | dict) -> UserDict:
        if isinstance(other, UserDict):
            return self.__class__(self.data | other.data)  # type: ignore
        if isinstance(other, dict):
            return self.__class__(self.data | other)  # type: ignore
        return NotImplemented

    def __ror__(self, other: UserDict | dict) -> UserDict:
        if isinstance(other, UserDict):
            return self.__class__(other.data | self.data)  # type: ignore
        if isinstance(other, dict):
            return self.__class__(other | self.data)  # type: ignore
        return NotImplemented

    def __ior__(self, other: UserDict | dict) -> UserDict:
        if isinstance(other, UserDict):
            self.data |= other.data  # type: ignore
        else:
            self.data |= other  # type: ignore
        return self

    def __copy__(self) -> UserDict:
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"].copy()
        return inst

    def copy(self) -> UserDict:
        if self.__class__ is UserDict:
            return UserDict(self.data.copy())  # type: ignore
        import copy

        data = self.data
        try:
            self.data = {}
            c = copy.copy(self)
        finally:
            self.data = data
        c.update(self)
        return c

    @classmethod
    def fromkeys(cls, iterable: Iterable, value: Optional[Any] = None) -> UserDict:
        d = cls()
        for key in iterable:
            d[key] = value
        return d


class SecretDict(UserDict):
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(******)"

    def __repr__(self) -> str:
        return str(self)


class Command(Enum):
    CHECK = "check"
    DISCOVER = "discover"
    READ = "read"
    READ_WITH_STATE = "read-with-state"
    SPEC = "spec"

    def needs_config(self) -> bool:
        return self in {Command.CHECK, Command.DISCOVER, Command.READ, Command.READ_WITH_STATE}

    def needs_catalog(self) -> bool:
        return self in {Command.READ, Command.READ_WITH_STATE}

    def needs_state(self) -> bool:
        return self in {Command.READ_WITH_STATE}


class TargetOrControl(Enum):
    TARGET = "target"
    CONTROL = "control"


class ActorType(Enum):
    SOURCE = "source"
    DESTINATION = "destination"


class ConnectionSubset(Enum):
    """Signals which connection pool to consider for this live test — just the Airbyte sandboxes, or all possible connctions on Cloud."""

    SANDBOXES = "sandboxes"
    ALL = "all"


@dataclass
class ConnectorUnderTest:
    """Represents a connector being tested.
    In validation tests, there would be one connector under test.
    When running regression tests, there would be two connectors under test: the target and the control versions of the same connector.
    """

    # connector image, assuming it's in the format "airbyte/{actor_type}-{connector_name}:{version}"
    image_name: str
    container: dagger.Container
    target_or_control: TargetOrControl

    @property
    def name(self) -> str:
        return self.image_name.replace("airbyte/", "").split(":")[0]

    @property
    def name_without_type_prefix(self) -> str:
        return self.name.replace(f"{self.actor_type.value}-", "")

    @property
    def version(self) -> str:
        return self.image_name.replace("airbyte/", "").split(":")[1]

    @property
    def actor_type(self) -> ActorType:
        if "airbyte/destination-" in self.image_name:
            return ActorType.DESTINATION
        elif "airbyte/source-" in self.image_name:
            return ActorType.SOURCE
        else:
            raise ValueError(
                f"Can't infer the actor type. Connector image name {self.image_name} does not contain 'airbyte/source' or 'airbyte/destination'"
            )

    @classmethod
    async def from_image_name(
        cls: type[ConnectorUnderTest],
        dagger_client: dagger.Client,
        image_name: str,
        target_or_control: TargetOrControl,
    ) -> ConnectorUnderTest:
        container = await get_connector_container(dagger_client, image_name)
        return cls(image_name, container, target_or_control)


@dataclass
class ExecutionInputs:
    hashed_connection_id: str
    connector_under_test: ConnectorUnderTest
    actor_id: str
    global_output_dir: Path
    command: Command
    config: Optional[SecretDict] = None
    configured_catalog: Optional[ConfiguredAirbyteCatalog] = None
    state: Optional[dict] = None
    environment_variables: Optional[dict] = None
    duckdb_path: Optional[Path] = None

    def raise_if_missing_attr_for_command(self, attribute: str) -> None:
        if getattr(self, attribute) is None:
            raise ValueError(f"We need a {attribute} to run the {self.command.value} command")

    def __post_init__(self) -> None:
        if self.command is Command.CHECK:
            self.raise_if_missing_attr_for_command("config")
        if self.command is Command.DISCOVER:
            self.raise_if_missing_attr_for_command("config")
        if self.command is Command.READ:
            self.raise_if_missing_attr_for_command("config")
            self.raise_if_missing_attr_for_command("configured_catalog")
        if self.command is Command.READ_WITH_STATE:
            self.raise_if_missing_attr_for_command("config")
            self.raise_if_missing_attr_for_command("configured_catalog")
            self.raise_if_missing_attr_for_command("state")

    @property
    def output_dir(self) -> Path:
        output_dir = (
            self.global_output_dir
            / f"command_execution_artifacts/{self.connector_under_test.name}/{self.command.value}/{self.connector_under_test.version}/{self.hashed_connection_id}"
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir


@dataclass
class ExecutionResult:
    hashed_connection_id: str
    actor_id: str
    configured_catalog: ConfiguredAirbyteCatalog
    connector_under_test: ConnectorUnderTest
    command: Command
    stdout_file_path: Path
    stderr_file_path: Path
    success: bool
    executed_container: Optional[dagger.Container]
    config: Optional[SecretDict]
    http_dump: Optional[dagger.File] = None
    http_flows: list[http.HTTPFlow] = field(default_factory=list)
    stream_schemas: Optional[dict[str, Any]] = None
    backend: Optional[FileBackend] = None

    HTTP_DUMP_FILE_NAME = "http_dump.mitm"
    HAR_FILE_NAME = "http_dump.har"

    @property
    def logger(self) -> logging.Logger:
        return logging.getLogger(f"{self.connector_under_test.target_or_control.value}-{self.command.value}")

    @property
    def airbyte_messages(self) -> Iterable[AirbyteMessage]:
        return self.parse_airbyte_messages_from_command_output(self.stdout_file_path)

    @property
    def duckdb_schema(self) -> Iterable[str]:
        return (self.connector_under_test.target_or_control.value, self.command.value, self.hashed_connection_id)

    @property
    def configured_streams(self) -> List[str]:
        return [stream.stream.name for stream in self.configured_catalog.streams]

    @property
    def primary_keys_per_stream(self) -> Dict[str, List[str]]:
        return {stream.stream.name: stream.primary_key[0] if stream.primary_key else None for stream in self.configured_catalog.streams}

    @classmethod
    async def load(
        cls: type[ExecutionResult],
        connector_under_test: ConnectorUnderTest,
        hashed_connection_id: str,
        actor_id: str,
        configured_catalog: ConfiguredAirbyteCatalog,
        command: Command,
        stdout_file_path: Path,
        stderr_file_path: Path,
        success: bool,
        executed_container: Optional[dagger.Container],
        config: Optional[SecretDict] = None,
        http_dump: Optional[dagger.File] = None,
    ) -> ExecutionResult:
        execution_result = cls(
            hashed_connection_id,
            actor_id,
            configured_catalog,
            connector_under_test,
            command,
            stdout_file_path,
            stderr_file_path,
            success,
            executed_container,
            config,
            http_dump,
        )
        await execution_result.load_http_flows()
        return execution_result

    async def load_http_flows(self) -> None:
        if not self.http_dump:
            return
        with tempfile.NamedTemporaryFile() as temp_file:
            await self.http_dump.export(temp_file.name)
            self.http_flows = get_http_flows_from_mitm_dump(Path(temp_file.name))

    def parse_airbyte_messages_from_command_output(
        self, command_output_path: Path, log_validation_errors: bool = False
    ) -> Iterable[AirbyteMessage]:
        with open(command_output_path) as command_output:
            for line in command_output:
                try:
                    yield AirbyteMessage.parse_raw(line)
                except ValidationError as e:
                    if log_validation_errors:
                        self.logger.warn(f"Error parsing AirbyteMessage: {e}")

    def get_records(self) -> Iterable[AirbyteMessage]:
        self.logger.info(
            f"Reading records all records for command {self.command.value} on {self.connector_under_test.target_or_control.value} version."
        )
        for message in self.airbyte_messages:
            if message.type is AirbyteMessageType.RECORD:
                yield message

    def generate_stream_schemas(self) -> dict[str, Any]:
        self.logger.info("Generating stream schemas")
        stream_builders: dict[str, SchemaBuilder] = {}
        for record in self.get_records():
            stream = record.record.stream
            if stream not in stream_builders:
                stream_schema_builder = SchemaBuilder()
                stream_schema_builder.add_schema({"type": "object", "properties": {}})
                stream_builders[stream] = stream_schema_builder
            stream_builders[stream].add_object(self.get_obfuscated_types(record.record.data))
        self.logger.info("Stream schemas generated")
        return {stream: sort_dict_keys(stream_builders[stream].to_schema()) for stream in stream_builders}

    @staticmethod
    def get_obfuscated_types(data: dict[str, Any]) -> dict[str, Any]:
        """
        Convert obfuscated records into a record whose values have the same type as the original values.
        """
        types = {}
        for k, v in data.items():
            if v.startswith("string_"):
                types[k] = "a"
            elif v.startswith("integer_"):
                types[k] = 0
            elif v.startswith("number_"):
                types[k] = 0.1
            elif v.startswith("boolean_"):
                types[k] = True
            elif v.startswith("null_"):
                types[k] = None
            elif v.startswith("array_"):
                types[k] = []
            elif v.startswith("object_"):
                types[k] = {}
            else:
                types[k] = v

        return types

    def get_records_per_stream(self, stream: str) -> Iterator[AirbyteMessage]:
        assert self.backend is not None, "Backend must be set to get records per stream"
        self.logger.info(f"Reading records for stream {stream}")
        if stream not in self.backend.record_per_stream_paths:
            self.logger.warning(f"No records found for stream {stream}")
            yield from []
        else:
            for message in self.parse_airbyte_messages_from_command_output(
                self.backend.record_per_stream_paths[stream], log_validation_errors=True
            ):
                if message.type is AirbyteMessageType.RECORD:
                    yield message

    def get_states_per_stream(self, stream: str) -> Dict[str, List[AirbyteStateMessage]]:
        self.logger.info(f"Reading state messages for stream {stream}")
        states = defaultdict(list)
        for message in self.airbyte_messages:
            if message.type is AirbyteMessageType.STATE:
                states[message.state.stream.stream_descriptor.name].append(message.state)
        return states

    def get_status_messages_per_stream(self, stream: str) -> Dict[str, List[AirbyteStreamStatusTraceMessage]]:
        self.logger.info(f"Reading state messages for stream {stream}")
        statuses = defaultdict(list)
        for message in self.airbyte_messages:
            if message.type is AirbyteMessageType.TRACE and message.trace.type == TraceType.STREAM_STATUS:
                statuses[message.trace.stream_status.stream_descriptor.name].append(message.trace.stream_status)
        return statuses

    @cache
    def get_message_count_per_type(self) -> dict[AirbyteMessageType, int]:
        message_count: dict[AirbyteMessageType, int] = defaultdict(int)
        for message in self.airbyte_messages:
            message_count[message.type] += 1
        return message_count

    async def save_http_dump(self, output_dir: Path) -> None:
        if self.http_dump:
            self.logger.info("An http dump was captured during the execution of the command, saving it.")
            http_dump_file_path = (output_dir / self.HTTP_DUMP_FILE_NAME).resolve()
            await self.http_dump.export(str(http_dump_file_path))
            self.logger.info(f"Http dump saved to {http_dump_file_path}")

            # Define where the har file will be saved
            har_file_path = (output_dir / self.HAR_FILE_NAME).resolve()
            # Convert the mitmproxy dump file to a har file
            mitm_http_stream_to_har(http_dump_file_path, har_file_path)
            self.logger.info(f"Har file saved to {har_file_path}")
        else:
            self.logger.warning("No http dump to save")

    def save_airbyte_messages(self, output_dir: Path, duckdb_path: Optional[Path] = None) -> None:
        self.logger.info("Saving Airbyte messages to disk")
        airbyte_messages_dir = output_dir / "airbyte_messages"
        airbyte_messages_dir.mkdir(parents=True, exist_ok=True)
        if duckdb_path:
            self.backend = DuckDbBackend(airbyte_messages_dir, duckdb_path, self.duckdb_schema)
        else:
            self.backend = FileBackend(airbyte_messages_dir)
        self.backend.write(self.airbyte_messages)
        self.logger.info("Airbyte messages saved")

    def save_stream_schemas(self, output_dir: Path) -> None:
        self.stream_schemas = self.generate_stream_schemas()
        stream_schemas_dir = output_dir / "stream_schemas"
        stream_schemas_dir.mkdir(parents=True, exist_ok=True)
        for stream_name, stream_schema in self.stream_schemas.items():
            (stream_schemas_dir / f"{sanitize_stream_name(stream_name)}.json").write_text(json.dumps(stream_schema, sort_keys=True))
        self.logger.info("Stream schemas saved to disk")

    async def save_artifacts(self, output_dir: Path, duckdb_path: Optional[Path] = None) -> None:
        self.logger.info("Saving artifacts to disk")
        self.save_airbyte_messages(output_dir, duckdb_path)
        self.update_configuration()
        await self.save_http_dump(output_dir)
        self.save_stream_schemas(output_dir)
        self.logger.info("All artifacts saved to disk")

    def get_updated_configuration(self, control_message_path: Path) -> Optional[dict[str, Any]]:
        """Iterate through the control messages to find CONNECTOR_CONFIG message and return the last updated configuration."""
        if not control_message_path.exists():
            return None
        updated_config = None
        for line in control_message_path.read_text().splitlines():
            if line.strip():
                connector_config = json.loads(line.strip()).get("connectorConfig", {})
                if connector_config:
                    updated_config = connector_config
        return updated_config

    def update_configuration(self) -> None:
        """This function checks if a configuration has to be updated by reading the control messages file.
        If a configuration has to be updated, it updates the configuration on the actor using the Airbyte API.
        """
        assert self.backend is not None, "Backend must be set to update configuration in order to find the control messages path"
        updated_configuration = self.get_updated_configuration(self.backend.jsonl_controls_path)
        if updated_configuration is None:
            return

        self.logger.warning(f"Updating configuration for {self.connector_under_test.name}, actor {self.actor_id}")
        url = f"https://api.airbyte.com/v1/{self.connector_under_test.actor_type.value}s/{self.actor_id}"

        payload = {
            "configuration": {
                **updated_configuration,
                f"{self.connector_under_test.actor_type.value}Type": self.connector_under_test.name_without_type_prefix,
            }
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {get_airbyte_api_key()}",
        }

        response = requests.patch(url, json=payload, headers=headers)
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            self.logger.error(f"Failed to update {self.connector_under_test.name} configuration on actor {self.actor_id}: {e}")
            self.logger.error(f"Response: {response.text}")
        self.logger.info(f"Updated configuration for {self.connector_under_test.name}, actor {self.actor_id}")

    def __hash__(self):
        return hash(self.connector_under_test.version)


@dataclass(kw_only=True)
class ConnectionObjects:
    source_config: Optional[SecretDict]
    destination_config: Optional[SecretDict]
    configured_catalog: Optional[ConfiguredAirbyteCatalog]
    catalog: Optional[AirbyteCatalog]
    state: Optional[dict]
    workspace_id: Optional[str]
    source_id: Optional[str]
    destination_id: Optional[str]
    source_docker_image: Optional[str]
    connection_id: Optional[str]

    @property
    def url(self) -> Optional[str]:
        if not self.workspace_id or not self.connection_id:
            return None
        return f"https://cloud.airbyte.com/workspaces/{self.workspace_id}/connections/{self.connection_id}"

    @property
    def hashed_connection_id(self) -> Optional[str]:
        if not self.connection_id:
            return None
        return hashlib.sha256(self.connection_id.encode("utf-8")).hexdigest()[:7]
