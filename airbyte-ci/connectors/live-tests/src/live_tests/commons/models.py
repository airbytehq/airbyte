# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import _collections_abc
import dagger
from airbyte_protocol.models import AirbyteMessage  # type: ignore
from airbyte_protocol.models import ConfiguredAirbyteCatalog  # type: ignore
from live_tests.commons.backends import FileBackend
from pydantic import ValidationError


class UserDict(_collections_abc.MutableMapping):
    # Start by filling-out the abstract methods
    def __init__(self, dict=None, /, **kwargs):
        self.data = {}
        if dict is not None:
            self.update(dict)
        if kwargs:
            self.update(kwargs)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        self.data[key] = item

    def __delitem__(self, key):
        del self.data[key]

    def __iter__(self):
        return iter(self.data)

    # Modify __contains__ to work correctly when __missing__ is present
    def __contains__(self, key):
        return key in self.data

    # Now, add the methods in dicts but not in MutableMapping
    def __repr__(self):
        return repr(self.data)

    def __or__(self, other):
        if isinstance(other, UserDict):
            return self.__class__(self.data | other.data)
        if isinstance(other, dict):
            return self.__class__(self.data | other)
        return NotImplemented

    def __ror__(self, other):
        if isinstance(other, UserDict):
            return self.__class__(other.data | self.data)
        if isinstance(other, dict):
            return self.__class__(other | self.data)
        return NotImplemented

    def __ior__(self, other):
        if isinstance(other, UserDict):
            self.data |= other.data
        else:
            self.data |= other
        return self

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"].copy()
        return inst

    def copy(self):
        if self.__class__ is UserDict:
            return UserDict(self.data.copy())
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
    def fromkeys(cls, iterable, value=None):
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


@dataclass
class ConnectorUnderTest:
    image_name: str
    container: dagger.Container

    @property
    def name(self):
        return self.image_name.replace("airbyte/", "").split(":")[0]

    @property
    def version(self):
        return self.image_name.replace("airbyte/", "").split(":")[1]


@dataclass
class ExecutionInputs:
    connector_under_test: ConnectorUnderTest
    command: Command
    config: Optional[SecretDict] = None
    catalog: Optional[ConfiguredAirbyteCatalog] = None
    state: Optional[Dict] = None
    environment_variables: Optional[Dict] = None
    enable_http_cache: bool = True

    def to_dict(self) -> dict:
        return {
            "connector_under_test": self.connector_under_test,
            "command": self.command,
            "config": self.config,
            "catalog": self.catalog,
            "state": self.state,
            "environment_variables": self.environment_variables,
            "enable_http_cache": self.enable_http_cache,
        }

    def raise_if_missing_attr_for_command(self, attribute: str):
        if getattr(self, attribute) is None:
            raise ValueError(f"We need a {attribute} to run the {self.command.value} command")

    def __post_init__(self):
        if self.command is Command.CHECK:
            self.raise_if_missing_attr_for_command("config")
        if self.command is Command.DISCOVER:
            self.raise_if_missing_attr_for_command("config")
        if self.command is Command.READ:
            self.raise_if_missing_attr_for_command("config")
            self.raise_if_missing_attr_for_command("catalog")
        if self.command is Command.READ_WITH_STATE:
            self.raise_if_missing_attr_for_command("config")
            self.raise_if_missing_attr_for_command("catalog")
            self.raise_if_missing_attr_for_command("state")


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    executed_container: dagger.Container
    http_dump: Optional[dagger.File]
    airbyte_messages: List[AirbyteMessage] = field(default_factory=list)
    airbyte_messages_parsing_errors: List[Tuple[Exception, str]] = field(default_factory=list)

    def __post_init__(self):
        self.airbyte_messages, self.airbyte_messages_parsing_errors = self.parse_airbyte_messages_from_command_output(self.stdout)

    @staticmethod
    def parse_airbyte_messages_from_command_output(
        command_output: str,
    ) -> Tuple[List[AirbyteMessage], List[Tuple[Exception, str]]]:
        airbyte_messages: List[AirbyteMessage] = []
        parsing_errors: List[Tuple[Exception, str]] = []
        for line in command_output.splitlines():
            try:
                airbyte_messages.append(AirbyteMessage.parse_raw(line))
            except ValidationError as e:
                parsing_errors.append((e, line))
        return airbyte_messages, parsing_errors


@dataclass
class ExecutionReport:
    execution_inputs: ExecutionInputs
    execution_result: ExecutionResult
    created_at: int = field(default_factory=lambda: int(time.time()))

    @property
    def report_dir(self) -> str:
        return f"{self.created_at}/{self.execution_inputs.connector_under_test.name}/{self.execution_inputs.command.value}/{self.execution_inputs.connector_under_test.version}/"

    @property
    def stdout_filename(self):
        return "stdout.log"

    @property
    def stderr_filename(self):
        return "stderr.log"

    @property
    def http_dump_filename(self):
        return "http_dump.mitm"

    async def save_to_disk(self, output_dir: Path) -> None:
        final_dir = output_dir / self.report_dir
        final_dir.mkdir(parents=True, exist_ok=True)
        stdout_file_path = final_dir / self.stdout_filename
        stdout_file_path.write_text(self.execution_result.stdout)

        stderr_file_path = final_dir / self.stderr_filename
        stderr_file_path.write_text(self.execution_result.stderr)
        if self.execution_result.http_dump:
            http_dump_file_path = final_dir / self.http_dump_filename
            await self.execution_result.http_dump.export(str(http_dump_file_path.resolve()))
        # TODO merge ExecutionReport.save_to_disk and Backend.write?
        # Make backends use customizable
        airbyte_messages_dir = final_dir / "airbyte_messages"
        airbyte_messages_dir.mkdir(parents=True, exist_ok=True)
        await FileBackend(airbyte_messages_dir).write(self.execution_result.airbyte_messages)
