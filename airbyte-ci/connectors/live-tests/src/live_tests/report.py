# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
from __future__ import annotations

import datetime
import json
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
from live_tests.consts import MAX_LINES_IN_REPORT

if TYPE_CHECKING:
    import pytest
    from _pytest.config import Config
    from airbyte_protocol.models import SyncMode, Type  # type: ignore
    from live_tests.commons.models import Command, ExecutionResult


class ReportState(Enum):
    INITIALIZING = "initializing"
    RUNNING = "running"
    FINISHED = "finished"


class Report:
    TEMPLATE_NAME = "report.html.j2"

    SPEC_SECRET_MASK_URL = "https://connectors.airbyte.com/files/registries/v0/specs_secrets_mask.yaml"

    def __init__(self, path: Path, pytest_config: Config) -> None:
        self.path = path
        self.pytest_config = pytest_config
        self.connection_objects = pytest_config.stash[stash_keys.CONNECTION_OBJECTS]
        self.secret_properties = self.get_secret_properties()
        self.created_at = datetime.datetime.utcnow()
        self.updated_at = self.created_at
        self.control_execution_results_per_command: dict[Command, ExecutionResult] = {}
        self.target_execution_results_per_command: dict[Command, ExecutionResult] = {}
        self.test_results: list[dict[str, Any]] = []
        self.update(ReportState.INITIALIZING)

    def get_secret_properties(self) -> list:
        response = requests.get(self.SPEC_SECRET_MASK_URL)
        response.raise_for_status()
        return yaml.safe_load(response.text)["properties"]

    def update(self, state: ReportState = ReportState.RUNNING) -> None:
        self._state = state
        self.updated_at = datetime.datetime.utcnow()
        self.render()

    def add_control_execution_result(self, control_execution_result: ExecutionResult) -> None:
        self.control_execution_results_per_command[control_execution_result.command] = control_execution_result
        self.update()

    def add_target_execution_result(self, target_execution_result: ExecutionResult) -> None:
        self.target_execution_results_per_command[target_execution_result.command] = target_execution_result
        self.update()

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
            connection_url=self.pytest_config.stash[stash_keys.CONNECTION_URL],
            workspace_id=self.pytest_config.stash[stash_keys.CONNECTION_OBJECTS].workspace_id,
            connection_id=self.pytest_config.stash[stash_keys.CONNECTION_ID],
            connector_image=self.pytest_config.stash[stash_keys.CONNECTOR_IMAGE],
            control_version=self.pytest_config.stash[stash_keys.CONTROL_VERSION],
            target_version=self.pytest_config.stash[stash_keys.TARGET_VERSION],
            source_config=json.dumps(
                self.scrub_secrets_from_config(
                    deepcopy(self.connection_objects.source_config.data) if self.connection_objects.source_config else {}
                ),
                indent=2,
            ),
            state=json.dumps(
                self.connection_objects.state if self.connection_objects.state else {},
                indent=2,
            ),
            configured_catalog=self.connection_objects.configured_catalog.json(indent=2)
            if self.connection_objects.configured_catalog
            else {},
            catalog=self.connection_objects.catalog.json(indent=2) if self.connection_objects.catalog else {},
            message_count_per_type=self.get_message_count_per_type(),
            stream_coverage_metrics=self.get_stream_coverage_metrics(),
            untested_streams=self.get_untested_streams(),
            selected_streams=self.get_selected_streams(),
            sync_mode_coverage=self.get_sync_mode_coverage(),
            requested_urls_per_command=self.get_requested_urls_per_command(),
            http_metrics_per_command=self.get_http_metrics_per_command(),
            record_count_per_command_and_stream=self.get_record_count_per_stream(),
            test_results=self.test_results,
            max_lines=MAX_LINES_IN_REPORT,
        )
        self.path.write_text(rendered)

    def scrub_secrets_from_config(self, to_scrub: MutableMapping) -> MutableMapping:
        if isinstance(to_scrub, dict):
            for key, value in to_scrub.items():
                if key in self.secret_properties:
                    to_scrub[key] = "********"
                elif isinstance(value, dict):
                    to_scrub[key] = self.scrub_secrets_from_config(value)
        return to_scrub

    ### REPORT CONTENT HELPERS ###
    def get_stream_coverage_metrics(self) -> dict[str, str]:
        configured_catalog_stream_count = (
            len(self.connection_objects.configured_catalog.streams) if self.connection_objects.configured_catalog else 0
        )
        catalog_stream_count = len(self.connection_objects.catalog.streams) if self.connection_objects.catalog else 0
        return {
            "Available in catalog": str(catalog_stream_count),
            "In use (in configured catalog)": str(configured_catalog_stream_count),
            "Coverage": f"{(configured_catalog_stream_count / catalog_stream_count) * 100:.2f}%",
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

        catalog_streams = self.connection_objects.catalog.streams if self.connection_objects.catalog else []

        return [stream.name for stream in catalog_streams if stream.name not in streams_with_data]

    def get_selected_streams(self) -> dict[str, dict[str, SyncMode | bool]]:
        untested_streams = self.get_untested_streams()
        return (
            {
                configured_stream.stream.name: {
                    "sync_mode": configured_stream.sync_mode,
                    "has_data": configured_stream.stream.name not in untested_streams,
                }
                for configured_stream in sorted(
                    self.connection_objects.configured_catalog.streams,
                    key=lambda x: x.stream.name,
                )
            }
            if self.connection_objects.configured_catalog
            else {}
        )

    def get_sync_mode_coverage(self) -> dict[SyncMode, int]:
        count_per_sync_mode: dict[SyncMode, int] = defaultdict(int)
        for s in self.get_selected_streams().values():
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
