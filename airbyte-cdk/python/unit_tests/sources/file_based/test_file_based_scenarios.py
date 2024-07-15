#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from pathlib import PosixPath

import pytest
from _pytest.capture import CaptureFixture
from airbyte_cdk.sources.abstract_source import AbstractSource
from freezegun import freeze_time
from unit_tests.sources.file_based.scenarios.avro_scenarios import (
    avro_all_types_scenario,
    avro_file_with_double_as_number_scenario,
    multiple_avro_combine_schema_scenario,
    multiple_streams_avro_scenario,
    single_avro_scenario,
)
from unit_tests.sources.file_based.scenarios.check_scenarios import (
    error_empty_stream_scenario,
    error_listing_files_scenario,
    error_multi_stream_scenario,
    error_reading_file_scenario,
    error_record_validation_user_provided_schema_scenario,
    success_csv_scenario,
    success_extensionless_scenario,
    success_multi_stream_scenario,
    success_user_provided_schema_scenario,
)
from unit_tests.sources.file_based.scenarios.concurrent_incremental_scenarios import (
    multi_csv_different_timestamps_scenario_concurrent,
    multi_csv_include_missing_files_within_history_range_concurrent_cursor_is_newer,
    multi_csv_include_missing_files_within_history_range_concurrent_cursor_is_older,
    multi_csv_per_timestamp_scenario_concurrent,
    multi_csv_remove_old_files_if_history_is_full_scenario_concurrent_cursor_is_newer,
    multi_csv_remove_old_files_if_history_is_full_scenario_concurrent_cursor_is_older,
    multi_csv_same_timestamp_more_files_than_history_size_scenario_concurrent_cursor_is_newer,
    multi_csv_same_timestamp_more_files_than_history_size_scenario_concurrent_cursor_is_older,
    multi_csv_same_timestamp_scenario_concurrent,
    multi_csv_skip_file_if_already_in_history_concurrent,
    multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario_concurrent_cursor_is_newer,
    multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario_concurrent_cursor_is_older,
    multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario_concurrent_cursor_is_newer,
    multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario_concurrent_cursor_is_older,
    multi_csv_sync_recent_files_if_history_is_incomplete_scenario_concurrent_cursor_is_newer,
    multi_csv_sync_recent_files_if_history_is_incomplete_scenario_concurrent_cursor_is_older,
    single_csv_file_is_skipped_if_same_modified_at_as_in_history_concurrent,
    single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history_concurrent,
    single_csv_input_state_is_earlier_scenario_concurrent,
    single_csv_input_state_is_later_scenario_concurrent,
    single_csv_no_input_state_scenario_concurrent,
)
from unit_tests.sources.file_based.scenarios.csv_scenarios import (
    csv_analytics_scenario,
    csv_autogenerate_column_names_scenario,
    csv_custom_bool_values_scenario,
    csv_custom_delimiter_in_double_quotes_scenario,
    csv_custom_delimiter_with_escape_char_scenario,
    csv_custom_format_scenario,
    csv_custom_null_values_scenario,
    csv_double_quote_is_set_scenario,
    csv_escape_char_is_set_scenario,
    csv_multi_stream_scenario,
    csv_newline_in_values_not_quoted_scenario,
    csv_newline_in_values_quoted_value_scenario,
    csv_no_files_scenario,
    csv_no_records_scenario,
    csv_single_stream_scenario,
    csv_skip_after_header_scenario,
    csv_skip_before_and_after_header_scenario,
    csv_skip_before_header_scenario,
    csv_string_are_not_null_if_strings_can_be_null_is_false_scenario,
    csv_string_can_be_null_with_input_schemas_scenario,
    csv_string_not_null_if_no_null_values_scenario,
    csv_strings_can_be_null_not_quoted_scenario,
    earlier_csv_scenario,
    empty_schema_inference_scenario,
    invalid_csv_multi_scenario,
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
from unit_tests.sources.file_based.scenarios.jsonl_scenarios import (
    invalid_jsonl_scenario,
    jsonl_multi_stream_scenario,
    jsonl_user_input_schema_scenario,
    multi_jsonl_stream_n_bytes_exceeds_limit_for_inference,
    multi_jsonl_stream_n_file_exceeds_limit_for_inference,
    multi_jsonl_with_different_keys_scenario,
    schemaless_jsonl_multi_stream_scenario,
    schemaless_jsonl_scenario,
    single_jsonl_scenario,
)
from unit_tests.sources.file_based.scenarios.parquet_scenarios import (
    multi_parquet_scenario,
    parquet_file_with_decimal_as_float_scenario,
    parquet_file_with_decimal_as_string_scenario,
    parquet_file_with_decimal_no_config_scenario,
    parquet_various_types_scenario,
    parquet_with_invalid_config_scenario,
    single_parquet_scenario,
    single_partitioned_parquet_scenario,
)
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenario
from unit_tests.sources.file_based.scenarios.unstructured_scenarios import (
    corrupted_file_scenario,
    no_file_extension_unstructured_scenario,
    simple_markdown_scenario,
    simple_txt_scenario,
    simple_unstructured_scenario,
    unstructured_invalid_file_type_discover_scenario_no_skip,
    unstructured_invalid_file_type_discover_scenario_skip,
    unstructured_invalid_file_type_read_scenario,
)
from unit_tests.sources.file_based.scenarios.user_input_schema_scenarios import (
    multi_stream_user_input_schema_scenario_emit_nonconforming_records,
    multi_stream_user_input_schema_scenario_schema_is_invalid,
    multi_stream_user_input_schema_scenario_skip_nonconforming_records,
    single_stream_user_input_schema_scenario_emit_nonconforming_records,
    single_stream_user_input_schema_scenario_schema_is_invalid,
    single_stream_user_input_schema_scenario_skip_nonconforming_records,
    valid_multi_stream_user_input_schema_scenario,
    valid_single_stream_user_input_schema_scenario,
)
from unit_tests.sources.file_based.scenarios.validation_policy_scenarios import (
    emit_record_scenario_multi_stream,
    emit_record_scenario_single_stream,
    skip_record_scenario_multi_stream,
    skip_record_scenario_single_stream,
    wait_for_rediscovery_scenario_multi_stream,
    wait_for_rediscovery_scenario_single_stream,
)
from unit_tests.sources.file_based.test_scenarios import verify_check, verify_discover, verify_read, verify_spec

discover_failure_scenarios = [
    empty_schema_inference_scenario,
]

discover_success_scenarios = [
    csv_no_records_scenario,
    csv_multi_stream_scenario,
    csv_single_stream_scenario,
    invalid_csv_scenario,
    invalid_csv_multi_scenario,
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
    single_parquet_scenario,
    multi_parquet_scenario,
    parquet_various_types_scenario,
    parquet_file_with_decimal_no_config_scenario,
    parquet_file_with_decimal_as_string_scenario,
    parquet_file_with_decimal_as_float_scenario,
    schemaless_csv_scenario,
    schemaless_csv_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_multi_stream_scenario,
    schemaless_with_user_input_schema_fails_connection_check_scenario,
    single_stream_user_input_schema_scenario_schema_is_invalid,
    single_stream_user_input_schema_scenario_emit_nonconforming_records,
    single_stream_user_input_schema_scenario_skip_nonconforming_records,
    multi_stream_user_input_schema_scenario_emit_nonconforming_records,
    multi_stream_user_input_schema_scenario_skip_nonconforming_records,
    multi_stream_user_input_schema_scenario_schema_is_invalid,
    valid_multi_stream_user_input_schema_scenario,
    valid_single_stream_user_input_schema_scenario,
    single_jsonl_scenario,
    multi_jsonl_with_different_keys_scenario,
    multi_jsonl_stream_n_file_exceeds_limit_for_inference,
    multi_jsonl_stream_n_bytes_exceeds_limit_for_inference,
    invalid_jsonl_scenario,
    jsonl_multi_stream_scenario,
    jsonl_user_input_schema_scenario,
    schemaless_jsonl_scenario,
    schemaless_jsonl_multi_stream_scenario,
    csv_string_can_be_null_with_input_schemas_scenario,
    csv_string_are_not_null_if_strings_can_be_null_is_false_scenario,
    csv_string_not_null_if_no_null_values_scenario,
    csv_strings_can_be_null_not_quoted_scenario,
    csv_newline_in_values_quoted_value_scenario,
    csv_escape_char_is_set_scenario,
    csv_double_quote_is_set_scenario,
    csv_custom_delimiter_with_escape_char_scenario,
    csv_custom_delimiter_in_double_quotes_scenario,
    csv_skip_before_header_scenario,
    csv_skip_after_header_scenario,
    csv_skip_before_and_after_header_scenario,
    csv_custom_bool_values_scenario,
    csv_custom_null_values_scenario,
    single_avro_scenario,
    avro_all_types_scenario,
    multiple_avro_combine_schema_scenario,
    multiple_streams_avro_scenario,
    avro_file_with_double_as_number_scenario,
    csv_newline_in_values_not_quoted_scenario,
    csv_autogenerate_column_names_scenario,
    parquet_with_invalid_config_scenario,
    single_partitioned_parquet_scenario,
    simple_markdown_scenario,
    simple_txt_scenario,
    simple_unstructured_scenario,
    corrupted_file_scenario,
    no_file_extension_unstructured_scenario,
    unstructured_invalid_file_type_discover_scenario_no_skip,
    unstructured_invalid_file_type_discover_scenario_skip,
    unstructured_invalid_file_type_read_scenario,
    multi_csv_different_timestamps_scenario_concurrent,
    multi_csv_include_missing_files_within_history_range_concurrent_cursor_is_newer,
    multi_csv_include_missing_files_within_history_range_concurrent_cursor_is_older,
    multi_csv_per_timestamp_scenario_concurrent,
    multi_csv_remove_old_files_if_history_is_full_scenario_concurrent_cursor_is_newer,
    multi_csv_remove_old_files_if_history_is_full_scenario_concurrent_cursor_is_older,
    multi_csv_same_timestamp_more_files_than_history_size_scenario_concurrent_cursor_is_newer,
    multi_csv_same_timestamp_more_files_than_history_size_scenario_concurrent_cursor_is_older,
    multi_csv_same_timestamp_scenario_concurrent,
    multi_csv_skip_file_if_already_in_history_concurrent,
    multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario_concurrent_cursor_is_newer,
    multi_csv_sync_files_within_history_time_window_if_history_is_incomplete_different_timestamps_scenario_concurrent_cursor_is_older,
    multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario_concurrent_cursor_is_newer,
    multi_csv_sync_files_within_time_window_if_history_is_incomplete__different_timestamps_scenario_concurrent_cursor_is_older,
    multi_csv_sync_recent_files_if_history_is_incomplete_scenario_concurrent_cursor_is_newer,
    multi_csv_sync_recent_files_if_history_is_incomplete_scenario_concurrent_cursor_is_older,
    single_csv_file_is_skipped_if_same_modified_at_as_in_history_concurrent,
    single_csv_file_is_synced_if_modified_at_is_more_recent_than_in_history_concurrent,
    single_csv_input_state_is_earlier_scenario_concurrent,
    single_csv_input_state_is_later_scenario_concurrent,
    single_csv_no_input_state_scenario_concurrent,
    earlier_csv_scenario,
    csv_no_files_scenario,
]

discover_scenarios = discover_failure_scenarios + discover_success_scenarios

read_scenarios = discover_success_scenarios + [
    emit_record_scenario_multi_stream,
    emit_record_scenario_single_stream,
    skip_record_scenario_multi_stream,
    skip_record_scenario_single_stream,
    csv_analytics_scenario,
    wait_for_rediscovery_scenario_multi_stream,
    wait_for_rediscovery_scenario_single_stream,
]

spec_scenarios = [
    single_csv_scenario,
]

check_scenarios = [
    error_empty_stream_scenario,
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
    valid_single_stream_user_input_schema_scenario,
    single_avro_scenario,
    earlier_csv_scenario,
    csv_no_files_scenario,
]


@pytest.mark.parametrize("scenario", discover_scenarios, ids=[s.name for s in discover_scenarios])
def test_file_based_discover(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario[AbstractSource]) -> None:
    verify_discover(capsys, tmp_path, scenario)


@pytest.mark.parametrize("scenario", read_scenarios, ids=[s.name for s in read_scenarios])
@freeze_time("2023-06-09T00:00:00Z")
def test_file_based_read(scenario: TestScenario[AbstractSource]) -> None:
    verify_read(scenario)


@pytest.mark.parametrize("scenario", spec_scenarios, ids=[c.name for c in spec_scenarios])
def test_file_based_spec(capsys: CaptureFixture[str], scenario: TestScenario[AbstractSource]) -> None:
    verify_spec(capsys, scenario)


@pytest.mark.parametrize("scenario", check_scenarios, ids=[c.name for c in check_scenarios])
def test_file_based_check(capsys: CaptureFixture[str], tmp_path: PosixPath, scenario: TestScenario[AbstractSource]) -> None:
    verify_check(capsys, tmp_path, scenario)
