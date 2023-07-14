#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import PosixPath
from typing import Any, Mapping

import pytest
from _pytest.capture import CaptureFixture
from freezegun import freeze_time

from airbyte_cdk.testing import scenario_utils
from airbyte_cdk.testing.scenario_builder import TestScenario
from unit_tests.sources.file_based.scenarios.check_scenarios import (
    error_empty_stream_scenario,
    error_extension_mismatch_scenario,
    error_listing_files_scenario,
    error_multi_stream_scenario,
    error_reading_file_scenario,
    error_record_validation_user_provided_schema_scenario,
    success_csv_scenario,
    success_extensionless_scenario,
    success_multi_stream_scenario,
    success_user_provided_schema_scenario,
)
from unit_tests.sources.file_based.scenarios.csv_scenarios import (
    csv_custom_format_scenario,
    csv_multi_stream_scenario,
    csv_single_stream_scenario,
    empty_schema_inference_scenario,
    invalid_csv_scenario,
    multi_csv_scenario,
    multi_csv_stream_n_file_exceeds_limit_for_inference,
    multi_stream_custom_format,
    schemaless_csv_multi_stream_scenario,
    schemaless_csv_scenario,
    schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_scenario,
    single_csv_scenario,
)
from unit_tests.sources.file_based.scenarios.incremental_scenarios import (
    multi_csv_different_timestamps_scenario,
    multi_csv_include_missing_files_within_history_range,
    multi_csv_per_timestamp_scenario,
    multi_csv_remove_old_files_if_history_is_full_scenario,
    multi_csv_same_timestamp_more_files_than_history_size_scenario,
    multi_csv_same_timestamp_scenario,
    multi_csv_skip_file_if_already_in_history,
    multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario,
    multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario,
    multi_csv_sync_recent_files_if_history_is_incomplete_scenario,
    single_csv_file_is_skipped_if_same_modified_at_as_in_history,
    single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history,
    single_csv_input_state_is_earlier_scenario,
    single_csv_input_state_is_later_scenario,
    single_csv_no_input_state_scenario,
)
from unit_tests.sources.file_based.scenarios.parquet_scenarios import (
    multi_parquet_scenario,
    parquet_various_types_scenario,
    single_parquet_scenario,
)
from unit_tests.sources.file_based.scenarios.stripe_scenarios import stripe_scenario
from unit_tests.sources.file_based.scenarios.validation_policy_scenarios import (
    emit_record_scenario_multi_stream,
    emit_record_scenario_single_stream,
    invalid_validation_policy,
    no_validation_policy,
    skip_record_scenario_multi_stream,
    skip_record_scenario_single_stream,
    wait_for_rediscovery_scenario_multi_stream,
    wait_for_rediscovery_scenario_single_stream,
)

discover_scenarios = [
    csv_multi_stream_scenario,
    csv_single_stream_scenario,
    invalid_csv_scenario,
    single_csv_scenario,
    multi_csv_scenario,
    multi_csv_stream_n_file_exceeds_limit_for_inference,
    single_csv_input_state_is_earlier_scenario,
    single_csv_no_input_state_scenario,
    single_csv_input_state_is_later_scenario,
    multi_csv_same_timestamp_scenario,
    multi_csv_different_timestamps_scenario,
    multi_csv_per_timestamp_scenario,
    multi_csv_skip_file_if_already_in_history,
    multi_csv_include_missing_files_within_history_range,
    multi_csv_remove_old_files_if_history_is_full_scenario,
    multi_csv_same_timestamp_more_files_than_history_size_scenario,
    multi_csv_sync_recent_files_if_history_is_incomplete_scenario,
    multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario,
    multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario,
    single_csv_file_is_skipped_if_same_modified_at_as_in_history,
    single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history,
    csv_custom_format_scenario,
    multi_stream_custom_format,
    empty_schema_inference_scenario,
    single_parquet_scenario,
    multi_parquet_scenario,
    parquet_various_types_scenario,
    schemaless_csv_scenario,
    schemaless_csv_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_scenario,
]


@pytest.mark.parametrize("scenario", discover_scenarios, ids=[s.name for s in discover_scenarios])
def test_discover(capsys: CaptureFixture[str], tmp_path: PosixPath, json_spec: Mapping[str, Any], scenario: TestScenario) -> None:
    scenario_utils.test_discover(capsys, tmp_path, json_spec, scenario)


read_scenarios = discover_scenarios + [
    emit_record_scenario_multi_stream,
    emit_record_scenario_single_stream,
    invalid_validation_policy,
    no_validation_policy,
    skip_record_scenario_multi_stream,
    skip_record_scenario_single_stream,
    wait_for_rediscovery_scenario_multi_stream,
    wait_for_rediscovery_scenario_single_stream,
    stripe_scenario
]


@pytest.mark.parametrize("scenario", read_scenarios, ids=[s.name for s in read_scenarios])
@freeze_time("2023-06-09T00:00:00Z")
def test_read(capsys: CaptureFixture[str], tmp_path: PosixPath, json_spec: Mapping[str, Any], scenario: TestScenario) -> None:
    scenario_utils.test_read(capsys, tmp_path, json_spec, scenario)


check_scenarios = [
    error_empty_stream_scenario,
    error_extension_mismatch_scenario,
    error_listing_files_scenario,
    error_reading_file_scenario,
    error_record_validation_user_provided_schema_scenario,
    error_multi_stream_scenario,
    success_csv_scenario,
    success_extensionless_scenario,
    success_multi_stream_scenario,
    success_user_provided_schema_scenario,
    schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_scenario,
]


@pytest.mark.parametrize("scenario", check_scenarios, ids=[c.name for c in check_scenarios])
def test_check(capsys: CaptureFixture[str], tmp_path: PosixPath, json_spec: Mapping[str, Any], scenario: TestScenario) -> None:
    scenario_utils.test_check(capsys, tmp_path, json_spec, scenario)
