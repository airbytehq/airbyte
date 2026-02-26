#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
"""Smoke test source for destination regression testing.

This source generates synthetic test data covering common edge cases
that break destinations: type variations, null handling, naming edge cases,
schema variations, and batch size variations.

Predefined scenarios are always available. Additional scenarios can be
injected dynamically via the ``custom_scenarios`` config field.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources.source import Source

from source_smoke_test.scenarios import (
    _DEFAULT_LARGE_BATCH_COUNT,
    PREDEFINED_SCENARIOS,
    get_scenario_records,
)


if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping


logger = logging.getLogger("airbyte")


def _build_streams_from_scenarios(
    scenarios: list[dict[str, Any]],
) -> list[AirbyteStream]:
    """Build AirbyteStream objects from scenario definitions."""
    return [
        AirbyteStream(
            name=scenario["name"],
            json_schema=scenario["json_schema"],
            supported_sync_modes=[SyncMode.full_refresh],
            source_defined_cursor=False,
            source_defined_primary_key=scenario.get("primary_key"),
        )
        for scenario in scenarios
    ]


class SourceSmokeTest(Source):
    """Smoke test source for destination regression testing.

    Generates synthetic data across predefined scenarios that cover
    common destination failure patterns. Supports dynamic injection
    of additional scenarios via the ``custom_scenarios`` config field.
    """

    def spec(
        self,
        logger: logging.Logger,
    ) -> ConnectorSpecification:
        """Return the connector specification."""
        return ConnectorSpecification(
            documentationUrl="https://docs.airbyte.com/integrations/sources/smoke-test",
            connectionSpecification={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Smoke Test Source Spec",
                "type": "object",
                "required": [],
                "properties": {
                    "custom_scenarios": {
                        "type": "array",
                        "title": "Custom Test Scenarios",
                        "description": (
                            "Additional test scenarios to inject "
                            "at runtime. Each scenario defines a "
                            "stream name, JSON schema, and records."
                        ),
                        "items": {
                            "type": "object",
                            "required": [
                                "name",
                                "json_schema",
                                "records",
                            ],
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Stream name for this scenario.",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Human-readable description of this scenario.",
                                },
                                "json_schema": {
                                    "type": "object",
                                    "description": "JSON schema for the stream.",
                                },
                                "records": {
                                    "type": "array",
                                    "description": "Records to emit for this stream.",
                                    "items": {"type": "object"},
                                },
                                "primary_key": {
                                    "type": ["array", "null"],
                                    "description": (
                                        "Primary key definition "
                                        "(list of key paths) "
                                        "or null."
                                    ),
                                    "items": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                        },
                        "default": [],
                    },
                    "large_batch_record_count": {
                        "type": "integer",
                        "title": "Large Batch Record Count",
                        "description": (
                            "Number of records to generate for "
                            "the large_batch_stream scenario. "
                            "Set to 0 to skip this stream."
                        ),
                        "default": 1000,
                    },
                    "all_fast_streams": {
                        "type": "boolean",
                        "title": "All Fast Streams",
                        "description": (
                            "Include all fast (non-high-volume) "
                            "predefined streams."
                        ),
                        "default": True,
                    },
                    "all_slow_streams": {
                        "type": "boolean",
                        "title": "All Slow Streams",
                        "description": (
                            "Include all slow (high-volume) streams "
                            "such as large_batch_stream. These are "
                            "excluded by default to avoid incurring "
                            "the cost of large record sets."
                        ),
                        "default": False,
                    },
                    "scenario_filter": {
                        "type": "array",
                        "title": "Scenario Filter",
                        "description": (
                            "Specific scenario names to include. "
                            "These are unioned with the boolean-driven "
                            "sets (deduped). If omitted or empty, "
                            "only the boolean flags control selection."
                        ),
                        "items": {"type": "string"},
                        "default": [],
                    },
                },
            },
        )

    def _get_all_scenarios(
        self,
        config: Mapping[str, Any],
    ) -> list[dict[str, Any]]:
        """Combine predefined and custom scenarios.

        Selection logic:
        1. Boolean flags control groups: ``all_fast_streams``
           (default true) enables non-high-volume scenarios,
           ``all_slow_streams`` (default false) enables
           high-volume scenarios.
        2. ``scenario_filter`` names are unioned with the boolean sets.
        3. Custom scenarios are always included.
        4. The final list is deduplicated by name.
        """
        include_default = config.get("all_fast_streams", True)
        include_high_volume = config.get("all_slow_streams", False)
        scenario_filter: list[str] = config.get("scenario_filter", [])
        explicit_names: set[str] = set(scenario_filter)

        large_batch_count = config.get(
            "large_batch_record_count",
            _DEFAULT_LARGE_BATCH_COUNT,
        )

        scenarios: list[dict[str, Any]] = []
        seen_names: set[str] = set()

        for scenario in PREDEFINED_SCENARIOS:
            name = scenario["name"]
            is_high_volume = scenario.get("high_volume", False)

            included_by_flag = (include_high_volume and is_high_volume) or (
                include_default and not is_high_volume
            )
            if not included_by_flag and name not in explicit_names:
                continue

            s = dict(scenario)
            if name == "large_batch_stream" and large_batch_count != _DEFAULT_LARGE_BATCH_COUNT:
                s["record_count"] = large_batch_count

            if name not in seen_names:
                scenarios.append(s)
                seen_names.add(name)

        custom = config.get("custom_scenarios", [])
        if custom:
            for cs in custom:
                name = cs.get("name", "")
                if not name or not cs.get("json_schema"):
                    continue
                if name not in seen_names:
                    scenarios.append(
                        {
                            "name": name,
                            "description": cs.get(
                                "description",
                                "Custom injected scenario",
                            ),
                            "json_schema": cs["json_schema"],
                            "primary_key": cs.get("primary_key"),
                            "records": cs.get("records", []),
                        }
                    )
                    seen_names.add(name)

        return scenarios

    def check(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
    ) -> AirbyteConnectionStatus:
        """Validate the configuration."""
        custom = config.get("custom_scenarios", [])
        for i, scenario in enumerate(custom):
            if not scenario.get("name"):
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"Custom scenario at index {i} is missing 'name'.",
                )
            if not scenario.get("json_schema"):
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"Custom scenario '{scenario['name']}' is missing 'json_schema'.",
                )

        scenarios = self._get_all_scenarios(config)
        if not scenarios:
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message="No scenarios available. Check scenario_filter config.",
            )

        logger.info(f"Smoke test source check passed with {len(scenarios)} scenarios.")
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
    ) -> AirbyteCatalog:
        """Return the catalog with all test scenario streams."""
        scenarios = self._get_all_scenarios(config)
        streams = _build_streams_from_scenarios(scenarios)
        logger.info(f"Discovered {len(streams)} smoke test streams.")
        return AirbyteCatalog(streams=streams)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: list[Any] | None = None,
    ) -> Iterable[AirbyteMessage]:
        """Read records from selected smoke test streams."""
        selected_streams = {stream.stream.name for stream in catalog.streams}
        scenarios = self._get_all_scenarios(config)
        scenario_map = {s["name"]: s for s in scenarios}
        now_ms = int(time.time() * 1000)

        for stream_name in selected_streams:
            scenario = scenario_map.get(stream_name)
            if not scenario:
                logger.warning(f"Stream '{stream_name}' not found in scenarios, skipping.")
                continue

            records = get_scenario_records(scenario)
            logger.info(f"Emitting {len(records)} records for stream '{stream_name}'.")

            for record in records:
                yield AirbyteMessage(
                    type=Type.RECORD,
                    record=AirbyteRecordMessage(
                        stream=stream_name,
                        data=record,
                        emitted_at=now_ms,
                    ),
                )
