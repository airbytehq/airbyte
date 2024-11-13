# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import datetime
import json
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Iterable, MutableMapping
from copy import deepcopy
from enum import Enum
from functools import cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

import requests
import yaml
from jinja2 import Environment, PackageLoader, select_autoescape
from live_tests import stash_keys
from live_tests.commons.models import ConnectionObjects
from live_tests.consts import MAX_LINES_IN_REPORT

if TYPE_CHECKING:
    from typing import List

    import pytest
    from _pytest.config import Config
    from airbyte_protocol.models import AirbyteStream, ConfiguredAirbyteStream, SyncMode, Type  # type: ignore
    from live_tests.commons.models import Command, ExecutionResult


class ReportState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    FINISHED = "finished"


class BaseReport(ABC):
    TEMPLATE_NAME: str

    def __init__(self, path: Path, pytest_config: Config) -> None:
        self.path = path
        self.pytest_config = pytest_config
        self.created_at = datetime.datetime.utcnow()
        self.control_execution_results_per_command: dict[Command, ExecutionResult] = {}
        self.target_execution_results_per_command: dict[Command, ExecutionResult] = {}
        self._state = ReportState.INITIALIZING
    @abstractmethod
    def render(self) -> None:
        pass

    @property
    def all_connection_objects(self) -> List[ConnectionObjects]:
        return self.pytest_config.stash[stash_keys.ALL_CONNECTION_OBJECTS]

    # TODO rework to support multiple execution results per command
    def add_control_execution_result(self, control_execution_result: ExecutionResult) -> None:
        self.control_execution_results_per_command[control_execution_result.command] = control_execution_result
        self.update()

    def add_target_execution_result(self, target_execution_result: ExecutionResult) -> None:
        self.target_execution_results_per_command[target_execution_result.command] = target_execution_result
        self.update()

    def update(self, state: ReportState = ReportState.RUNNING) -> None:
        self._state = state
        self.updated_at = datetime.datetime.utcnow()
        self.render()

class PrivateDetailsReport(BaseReport):
    TEMPLATE_NAME = "private_details.html.j2"
    SPEC_SECRET_MASK_URL = "https://connectors.airbyte.com/files/registries/v0/specs_secrets_mask.yaml"

    def __init__(self, path: Path, pytest_config: Config) -> None:
        super().__init__(path, pytest_config)
        self.secret_properties = self.get_secret_properties()
        self.render()

    def get_secret_properties(self) -> list:
        response = requests.get(self.SPEC_SECRET_MASK_URL)
        response.raise_for_status()
        return yaml.safe_load(response.text)["properties"]

    def scrub_secrets_from_config(self, to_scrub: MutableMapping) -> MutableMapping:
        if isinstance(to_scrub, dict):
            for key, value in to_scrub.items():
                if key in self.secret_properties:
                    to_scrub[key] = "********"
                elif isinstance(value, dict):
                    to_scrub[key] = self.scrub_secrets_from_config(value)
        return to_scrub


    @property
    def renderable_connection_objects(self) -> list[dict[str, Any]]:
        return [
            {
                "workspace_id": connection_objects.workspace_id,
                "connection_id": connection_objects.connection_id,
                "hashed_connection_id": connection_objects.hashed_connection_id,
                "source_config": json.dumps(
                    self.scrub_secrets_from_config(
                        deepcopy(connection_objects.source_config.data) if connection_objects.source_config else {}
                    ),
                    indent=2,
                ),
                "url": connection_objects.url,
            }
            for connection_objects in self.all_connection_objects
        ]

    def render(self) -> None:
        jinja_env = Environment(
            loader=PackageLoader(__package__, "templates"),
            autoescape=select_autoescape(),
            trim_blocks=False,
            lstrip_blocks=True,
        )
        template = jinja_env.get_template(self.TEMPLATE_NAME)
        rendered = template.render(
            user=self.pytest_config.stash[stash_keys.USER],
            test_date=self.created_at,
            all_connection_objects=self.renderable_connection_objects,
            connector_image=self.pytest_config.stash[stash_keys.CONNECTOR_IMAGE],
            control_version=self.pytest_config.stash[stash_keys.CONTROL_VERSION],
            target_version=self.pytest_config.stash[stash_keys.TARGET_VERSION],
            requested_urls_per_command=self.get_requested_urls_per_command(),
            fully_generated=self._state is ReportState.FINISHED,
        )
        self.path.write_text(rendered)


    def get_requested_urls_per_command(
        self,
    ) -> dict[Command, list[tuple[int, str, str]]]:
        requested_urls_per_command = {}
        all_commands = sorted(
            list(set(self.control_execution_results_per_command.keys()).union(set(self.target_execution_results_per_command.keys()))),
            key=lambda command: command.value,
        )
        for command in all_commands:
            if command in self.control_execution_results_per_command:
                control_flows = self.control_execution_results_per_command[command].http_flows
            else:
                control_flows = []
            if command in self.target_execution_results_per_command:
                target_flows = self.target_execution_results_per_command[command].http_flows
            else:
                target_flows = []
            all_flows = []
            max_flows = max(len(control_flows), len(target_flows))
            for i in range(max_flows):
                control_url = control_flows[i].request.url if i < len(control_flows) else ""
                target_url = target_flows[i].request.url if i < len(target_flows) else ""
                all_flows.append((i, control_url, target_url))
            requested_urls_per_command[command] = all_flows
        return requested_urls_per_command


class TestReport(BaseReport):
    TEMPLATE_NAME = "report.html.j2"

    def __init__(self, path: Path, pytest_config: Config) -> None:
        super().__init__(path, pytest_config)
        self.updated_at = self.created_at
        self.test_results: list[dict[str, Any]] = []
        self.update(ReportState.INITIALIZING)

    # TODO: Remove this property once the test report can handle multiple connection objects
    @property
    def connection_objects(self) -> ConnectionObjects:
        return self.all_connection_objects[0]

    def update(self, state: ReportState = ReportState.RUNNING) -> None:
        self._state = state
        self.updated_at = datetime.datetime.utcnow()
        self.render()


    def add_test_result(self, test_report: pytest.TestReport, test_documentation: Optional[str] = None) -> None:
        cut_properties: list[tuple[str, str]] = []
        for property_name, property_value in test_report.user_properties:
            if len(str(property_value).splitlines()) > MAX_LINES_IN_REPORT:
                cut_property_name = f"{property_name} (truncated)"
                cut_property_value = "\n".join(str(property_value).splitlines()[:MAX_LINES_IN_REPORT])
                cut_property_value += f"\n... and {len(str(property_value).splitlines()) - MAX_LINES_IN_REPORT} more lines.\nPlease check the artifacts files for the full output."
                cut_properties.append((cut_property_name, cut_property_value))
            else:
                cut_properties.append((property_name, str(property_value)))
        self.test_results.append(
            {
                "name": test_report.head_line,
                "result": test_report.outcome,
                "output": test_report.longreprtext if test_report.longrepr else "",
                "properties": cut_properties,
                "documentation": test_documentation,
            }
        )
        self.update()

    def render(self) -> None:
        jinja_env = Environment(
            loader=PackageLoader(__package__, "templates"),
            autoescape=select_autoescape(),
            trim_blocks=False,
            lstrip_blocks=True,
        )
        template = jinja_env.get_template(self.TEMPLATE_NAME)
        rendered = template.render(
            fully_generated=self._state is ReportState.FINISHED,
            user=self.pytest_config.stash[stash_keys.USER],
            test_date=self.updated_at,
            connector_image=self.pytest_config.stash[stash_keys.CONNECTOR_IMAGE],
            control_version=self.pytest_config.stash[stash_keys.CONTROL_VERSION],
            target_version=self.pytest_config.stash[stash_keys.TARGET_VERSION],
            all_connection_objects=self.renderable_connection_objects,
            message_count_per_type=self.get_message_count_per_type(),
            stream_coverage_metrics=self.get_stream_coverage_metrics(),
            untested_streams=self.get_untested_streams(),
            selected_streams=self.get_configured_streams(),
            sync_mode_coverage=self.get_sync_mode_coverage(),
            http_metrics_per_command=self.get_http_metrics_per_command(),
            record_count_per_command_and_stream=self.get_record_count_per_stream(),
            test_results=self.test_results,
            max_lines=MAX_LINES_IN_REPORT,
        )
        self.path.write_text(rendered)

    @property
    def renderable_connection_objects(self) -> list[dict[str, Any]]:
        return [
            {
                "hashed_connection_id": connection_objects.hashed_connection_id,
                "catalog": connection_objects.catalog.json(indent=2) if connection_objects.catalog else {},
                "configured_catalog": connection_objects.configured_catalog.json(indent=2),
                "state": json.dumps(self.connection_objects.state if self.connection_objects.state else {}, indent=2),
            }
            for connection_objects in self.all_connection_objects
        ]

    def get_stream_coverage_metrics(self) -> dict[str, str]:

        configured_catalog_stream_count = self.get_configured_streams()
        catalog_stream_count = len(self.connection_objects.catalog.streams) if self.connection_objects.catalog else 0
        coverage = configured_catalog_stream_count / catalog_stream_count if catalog_stream_count > 0 else 0
        return {
            "Available in catalog": str(catalog_stream_count),
            "In use (in configured catalog)": str(configured_catalog_stream_count),
            "Coverage": f"{coverage:.2f}%",
        }

    def get_record_count_per_stream(
        self,
    ) -> dict[Command, dict[str, dict[str, int] | int]]:
        record_count_per_command_and_stream: dict[Command, dict[str, dict[str, int] | int]] = {}

        for control_result, target_result in zip(
            self.control_execution_results_per_command.values(),
            self.target_execution_results_per_command.values(),
            strict=False,
        ):
            per_stream_count = defaultdict(lambda: {"control": 0, "target": 0})  # type: ignore
            for result, source in [
                (control_result, "control"),
                (target_result, "target"),
            ]:
                stream_schemas: Iterable = result.stream_schemas or []

                for stream in stream_schemas:
                    per_stream_count[stream][source] = self._get_record_count_for_stream(result, stream)
            for stream in per_stream_count:
                per_stream_count[stream]["difference"] = per_stream_count[stream]["target"] - per_stream_count[stream]["control"]
            record_count_per_command_and_stream[control_result.command] = per_stream_count  # type: ignore

        return record_count_per_command_and_stream

    @cache
    def _get_record_count_for_stream(self, result: ExecutionResult, stream: str) -> int:
        return sum(1 for _ in result.get_records_per_stream(stream))  # type: ignore

    def get_untested_streams(self) -> list[str]:
        streams_with_data: set[str] = set()
        for stream_count in self.get_record_count_per_stream().values():
            streams_with_data.update(stream_count.keys())

        return [stream.name for stream in self.all_streams if stream.name not in streams_with_data]

    @property
    def all_streams(self) -> List[AirbyteStream]:
        # A set would be better but AirbyteStream is not hashable
        all_streams = dict()
        for connection_objects in self.all_connection_objects:
            if connection_objects.catalog:
                for stream in connection_objects.catalog.streams:
                    all_streams[stream.name] = stream
        return list(all_streams.values())
    
    @property
    def all_configured_streams(self) -> List[ConfiguredAirbyteStream]:
        all_configured_streams = dict()
        for connection_objects in self.all_connection_objects:
            if connection_objects.configured_catalog:
                for configured_airbyte_stream in connection_objects.configured_catalog.streams:
                    all_configured_streams[configured_airbyte_stream.stream.name] = configured_airbyte_stream
        return list(all_configured_streams.values())
    
    def get_configured_streams(self) -> dict[str, dict[str, SyncMode | bool]]:
        untested_streams = self.get_untested_streams()
        return (
            {
                configured_stream.stream.name: {
                    "sync_mode": configured_stream.sync_mode,
                    "has_data": configured_stream.stream.name not in untested_streams,
                }
                for configured_stream in sorted(
                    self.all_configured_streams,
                    key=lambda x: x.stream.name,
                )
            }
            if self.all_configured_streams
            else {}
        )

    def get_sync_mode_coverage(self) -> dict[SyncMode, int]:
        count_per_sync_mode: dict[SyncMode, int] = defaultdict(int)
        for s in self.get_configured_streams().values():
            count_per_sync_mode[s["sync_mode"]] += 1
        return count_per_sync_mode

    def get_message_count_per_type(
        self,
    ) -> tuple[list[Command], dict[Type, dict[Command, dict[str, int]]]]:
        message_count_per_type_and_command: dict[Type, dict[Command, dict[str, int]]] = {}
        all_message_types = set()
        all_commands = set()
        # Gather all message types from both control and target execution reports
        for execution_results_per_command in [
            self.control_execution_results_per_command,
            self.target_execution_results_per_command,
        ]:
            for command, execution_result in execution_results_per_command.items():
                all_commands.add(command)
                for message_type in execution_result.get_message_count_per_type().keys():
                    all_message_types.add(message_type)

        all_commands_sorted = sorted(all_commands, key=lambda command: command.value)
        all_message_types_sorted = sorted(all_message_types, key=lambda message_type: message_type.value)

        # Iterate over all message types and commands to count messages
        for message_type in all_message_types_sorted:
            message_count_per_type_and_command[message_type] = {}
            for command in all_commands_sorted:
                message_count_per_type_and_command[message_type][command] = {
                    "control": 0,
                    "target": 0,
                }
                if command in self.control_execution_results_per_command:
                    message_count_per_type_and_command[message_type][command]["control"] = (
                        self.control_execution_results_per_command[command].get_message_count_per_type().get(message_type, 0)
                    )
                if command in self.target_execution_results_per_command:
                    message_count_per_type_and_command[message_type][command]["target"] = (
                        self.target_execution_results_per_command[command].get_message_count_per_type().get(message_type, 0)
                    )
                message_count_per_type_and_command[message_type][command]["difference"] = (
                    message_count_per_type_and_command[message_type][command]["target"]
                    - message_count_per_type_and_command[message_type][command]["control"]
                )
        return all_commands_sorted, message_count_per_type_and_command

    def get_http_metrics_per_command(
        self,
    ) -> dict[Command, dict[str, dict[str, int | str] | int]]:
        metrics_per_command: dict[Command, dict[str, dict[str, int | str] | int]] = {}

        for control_result, target_result in zip(
            self.control_execution_results_per_command.values(),
            self.target_execution_results_per_command.values(),
            strict=False,
        ):
            control_flow_count = len(control_result.http_flows)
            control_all_urls = [f.request.url for f in control_result.http_flows]
            control_duplicate_flow_count = len(control_all_urls) - len(set(control_all_urls))
            control_cache_hits_count = sum(1 for f in control_result.http_flows if f.is_replay)
            control_cache_hit_ratio = f"{(control_cache_hits_count / control_flow_count) * 100:.2f}%" if control_flow_count != 0 else "N/A"

            target_flow_count = len(target_result.http_flows)
            target_all_urls = [f.request.url for f in target_result.http_flows]
            target_duplicate_flow_count = len(target_all_urls) - len(set(target_all_urls))
            target_cache_hits_count = sum(1 for f in target_result.http_flows if f.is_replay)
            target_cache_hit_ratio = f"{(target_cache_hits_count / target_flow_count) * 100:.2f}%" if target_flow_count != 0 else "N/A"

            flow_count_difference = target_flow_count - control_flow_count

            metrics_per_command[control_result.command] = {
                "control": {
                    "flow_count": control_flow_count,
                    "duplicate_flow_count": control_duplicate_flow_count,
                    "cache_hits_count": control_cache_hits_count,
                    "cache_hit_ratio": control_cache_hit_ratio,
                },
                "target": {
                    "flow_count": target_flow_count,
                    "duplicate_flow_count": target_duplicate_flow_count,
                    "cache_hits_count": target_cache_hits_count,
                    "cache_hit_ratio": target_cache_hit_ratio,
                },
                "difference": flow_count_difference,
            }

        return metrics_per_command
