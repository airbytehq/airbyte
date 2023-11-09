#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from airbyte_cdk.sources.streams.concurrent.cursor import CursorField
from airbyte_cdk.sources.streams.concurrent.state_converter import ConcurrencyCompatibleStateType
from unit_tests.sources.file_based.scenarios.scenario_builder import IncrementalScenarioConfig, TestScenarioBuilder
from unit_tests.sources.streams.concurrent.scenarios.stream_facade_builder import StreamFacadeSourceBuilder
from unit_tests.sources.streams.concurrent.scenarios.utils import MockStream

_NO_SLICE_BOUNDARIES = None
_NO_INPUT_STATE = []
test_incremental_stream_without_slice_boundaries_no_input_state = (
    TestScenarioBuilder()
    .set_name("test_incremental_stream_without_slice_boundaries_no_input_state")
    .set_config({})
    .set_source_builder(
        StreamFacadeSourceBuilder()
        .set_streams(
            [
                MockStream(
                    [
                        ({"from": 0, "to": 1}, [{"id": "1", "cursor_field": 0}, {"id": "2", "cursor_field": 1}]),
                        ({"from": 1, "to": 2}, [{"id": "3", "cursor_field": 2}, {"id": "4", "cursor_field": 3}]),
                    ],
                    "stream1",
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                )
            ]
        )
        .set_incremental(CursorField("cursor_field"), _NO_SLICE_BOUNDARIES)
        .set_input_state(_NO_INPUT_STATE)
    )
    .set_expected_read_error(ValueError, "test exception")
    .set_log_levels({"ERROR", "WARN", "WARNING", "INFO", "DEBUG"})
    .set_incremental_scenario_config(IncrementalScenarioConfig(input_state=_NO_INPUT_STATE))
    .build()
)


test_incremental_stream_with_slice_boundaries_no_input_state = (
    TestScenarioBuilder()
    .set_name("test_incremental_stream_with_slice_boundaries_no_input_state")
    .set_config({})
    .set_source_builder(
        StreamFacadeSourceBuilder()
        .set_streams(
            [
                MockStream(
                    [
                        ({"from": 0, "to": 1}, [{"id": "1", "cursor_field": 0}, {"id": "2", "cursor_field": 1}]),
                        ({"from": 1, "to": 2}, [{"id": "3", "cursor_field": 2}, {"id": "4", "cursor_field": 3}]),
                    ],
                    "stream1",
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                )
            ]
        )
        .set_incremental(CursorField("cursor_field"), ("from", "to"))
        .set_input_state(_NO_INPUT_STATE)
    )
    .set_expected_records(
        [
            {"data": {"id": "1", "cursor_field": 0}, "stream": "stream1"},
            {"data": {"id": "2", "cursor_field": 1}, "stream": "stream1"},
            {"stream1": {"slices": [{"start": 0, "end": 1}], "state_type": ConcurrencyCompatibleStateType.date_range.value, "legacy": {}}},
            {"data": {"id": "3", "cursor_field": 2}, "stream": "stream1"},
            {"data": {"id": "4", "cursor_field": 3}, "stream": "stream1"},
            {"stream1": {"slices": [{"start": 0, "end": 2}], "state_type": ConcurrencyCompatibleStateType.date_range.value, "legacy": {}}},
        ]
    )
    .set_log_levels({"ERROR", "WARN", "WARNING", "INFO", "DEBUG"})
    .set_incremental_scenario_config(IncrementalScenarioConfig(input_state=_NO_INPUT_STATE))
    .build()
)


LEGACY_STATE = [{"type": "STREAM", "stream": {"stream_state": {"created": 0}, "stream_descriptor": {"name": "stream1"}}}]
test_incremental_stream_without_slice_boundaries_with_legacy_state = (
    TestScenarioBuilder()
    .set_name("test_incremental_stream_without_slice_boundaries_with_legacy_state")
    .set_config({})
    .set_source_builder(
        StreamFacadeSourceBuilder()
        .set_streams(
            [
                MockStream(
                    [
                        ({"from": 0, "to": 1}, [{"id": "1", "cursor_field": 0}, {"id": "2", "cursor_field": 1}]),
                        ({"from": 1, "to": 2}, [{"id": "3", "cursor_field": 2}, {"id": "4", "cursor_field": 3}]),
                    ],
                    "stream1",
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                )
            ]
        )
        .set_incremental(CursorField("cursor_field"), _NO_SLICE_BOUNDARIES)
        .set_input_state(LEGACY_STATE)
    )
    .set_expected_read_error(ValueError, "test exception")
    .set_log_levels({"ERROR", "WARN", "WARNING", "INFO", "DEBUG"})
    .set_incremental_scenario_config(IncrementalScenarioConfig(input_state=LEGACY_STATE))
    .build()
)


test_incremental_stream_with_slice_boundaries_with_legacy_state = (
    TestScenarioBuilder()
    .set_name("test_incremental_stream_with_slice_boundaries_with_legacy_state")
    .set_config({})
    .set_source_builder(
        StreamFacadeSourceBuilder()
        .set_streams(
            [
                MockStream(
                    [
                        ({"from": 0, "to": 1}, [{"id": "1", "cursor_field": 0}, {"id": "2", "cursor_field": 1}]),
                        ({"from": 1, "to": 2}, [{"id": "3", "cursor_field": 2}, {"id": "4", "cursor_field": 3}]),
                    ],
                    "stream1",
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                )
            ]
        )
        .set_incremental(CursorField(["cursor_field"]), ("from", "to"))
        .set_input_state(LEGACY_STATE)
    )
    .set_expected_records(
        [
            {"data": {"id": "1", "cursor_field": 0}, "stream": "stream1"},
            {"data": {"id": "2", "cursor_field": 1}, "stream": "stream1"},
            {
                "stream1": {
                    "slices": [{"start": 0, "end": 1}],
                    "state_type": ConcurrencyCompatibleStateType.date_range.value,
                    "legacy": {"created": 0},
                }
            },
            {"data": {"id": "3", "cursor_field": 2}, "stream": "stream1"},
            {"data": {"id": "4", "cursor_field": 3}, "stream": "stream1"},
            {
                "stream1": {
                    "slices": [{"start": 0, "end": 2}],
                    "state_type": ConcurrencyCompatibleStateType.date_range.value,
                    "legacy": {"created": 0},
                }
            },
        ]
    )
    .set_log_levels({"ERROR", "WARN", "WARNING", "INFO", "DEBUG"})
    .set_incremental_scenario_config(IncrementalScenarioConfig(input_state=LEGACY_STATE))
    .build()
)


CONCURRENT_STATE = [
    {
        "type": "STREAM",
        "stream": {
            "stream_state": {
                "slices": [{"start": 0, "end": 0}],
                "state_type": ConcurrencyCompatibleStateType.date_range.value,
            },
            "stream_descriptor": {"name": "stream1"},
        },
    },
]
test_incremental_stream_without_slice_boundaries_with_concurrent_state = (
    TestScenarioBuilder()
    .set_name("test_incremental_stream_without_slice_boundaries_with_concurrent_state")
    .set_config({})
    .set_source_builder(
        StreamFacadeSourceBuilder()
        .set_streams(
            [
                MockStream(
                    [
                        ({"from": 0, "to": 1}, [{"id": "1", "cursor_field": 0}, {"id": "2", "cursor_field": 1}]),
                        ({"from": 1, "to": 2}, [{"id": "3", "cursor_field": 2}, {"id": "4", "cursor_field": 3}]),
                    ],
                    "stream1",
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                )
            ]
        )
        .set_incremental(CursorField("cursor_field"), _NO_SLICE_BOUNDARIES)
        .set_input_state(CONCURRENT_STATE)
    )
    .set_expected_read_error(ValueError, "test exception")
    .set_log_levels({"ERROR", "WARN", "WARNING", "INFO", "DEBUG"})
    .set_incremental_scenario_config(IncrementalScenarioConfig(input_state=CONCURRENT_STATE))
    .build()
)


test_incremental_stream_with_slice_boundaries_with_concurrent_state = (
    TestScenarioBuilder()
    .set_name("test_incremental_stream_with_slice_boundaries_with_concurrent_state")
    .set_config({})
    .set_source_builder(
        StreamFacadeSourceBuilder()
        .set_streams(
            [
                MockStream(
                    [
                        ({"from": 0, "to": 1}, [{"id": "1", "cursor_field": 0}, {"id": "2", "cursor_field": 1}]),
                        ({"from": 1, "to": 2}, [{"id": "3", "cursor_field": 2}, {"id": "4", "cursor_field": 3}]),
                    ],
                    "stream1",
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                )
            ]
        )
        .set_incremental(CursorField(["cursor_field"]), ("from", "to"))
        .set_input_state(CONCURRENT_STATE)
    )
    .set_expected_records(
        [
            {"data": {"id": "1", "cursor_field": 0}, "stream": "stream1"},
            {"data": {"id": "2", "cursor_field": 1}, "stream": "stream1"},
            {"stream1": {"slices": [{"start": 0, "end": 1}], "state_type": ConcurrencyCompatibleStateType.date_range.value}},
            {"data": {"id": "3", "cursor_field": 2}, "stream": "stream1"},
            {"data": {"id": "4", "cursor_field": 3}, "stream": "stream1"},
            {"stream1": {"slices": [{"start": 0, "end": 2}], "state_type": ConcurrencyCompatibleStateType.date_range.value}},
        ]
    )
    .set_log_levels({"ERROR", "WARN", "WARNING", "INFO", "DEBUG"})
    .set_incremental_scenario_config(IncrementalScenarioConfig(input_state=CONCURRENT_STATE))
    .build()
)
