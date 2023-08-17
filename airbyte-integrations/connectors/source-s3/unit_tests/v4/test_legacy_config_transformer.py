#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_s3.source import SourceS3Spec
from source_s3.v4.legacy_config_transformer import LegacyConfigTransformer


@pytest.mark.parametrize(
    "legacy_config, expected_config",
    [
        pytest.param(
            {
                "dataset": "test_data",
                "provider": {
                    "storage": "S3",
                    "bucket": "test_bucket",
                    "aws_access_key_id": "some_access_key",
                    "aws_secret_access_key": "some_secret",
                    "endpoint": "https://external-s3.com",
                    "path_prefix": "a_folder/",
                    "start_date": "2022-01-01T01:02:03Z",
                },
                "format": {
                    "filetype": "avro",
                },
                "path_pattern": "**/*.avro",
                "schema": '{"col1": "string", "col2": "integer"}',
            },
            {
                "bucket": "test_bucket",
                "aws_access_key_id": "some_access_key",
                "aws_secret_access_key": "some_secret",
                "endpoint": "https://external-s3.com",
                "start_date": "2022-01-01T01:02:03.000000Z",
                "streams": [
                    {
                        "name": "test_data",
                        "file_type": "avro",
                        "globs": ["**/*.avro"],
                        "legacy_prefix": "a_folder/",
                        "validation_policy": "Emit Record",
                        "input_schema": '{"col1": "string", "col2": "integer"}',
                        "format": {"filetype": "avro"},
                    }
                ],
            },
            id="test_convert_legacy_config",
        ),
        pytest.param(
            {
                "dataset": "test_data",
                "provider": {
                    "storage": "S3",
                    "bucket": "test_bucket",
                },
                "format": {
                    "filetype": "avro",
                },
                "path_pattern": "**/*.avro",
            },
            {
                "bucket": "test_bucket",
                "streams": [
                    {
                        "name": "test_data",
                        "file_type": "avro",
                        "globs": ["**/*.avro"],
                        "legacy_prefix": "",
                        "validation_policy": "Emit Record",
                        "format": {"filetype": "avro"},
                    }
                ],
            },
            id="test_convert_no_optional_fields",
        ),
        pytest.param(
            {
                "dataset": "test_data",
                "provider": {
                    "storage": "S3",
                    "bucket": "test_bucket",
                    "path_prefix": "a_prefix/",
                },
                "format": {
                    "filetype": "avro",
                },
                "path_pattern": "*.csv|**/*",
            },
            {
                "bucket": "test_bucket",
                "streams": [
                    {
                        "name": "test_data",
                        "file_type": "avro",
                        "globs": ["*.csv", "**/*"],
                        "validation_policy": "Emit Record",
                        "legacy_prefix": "a_prefix/",
                        "format": {"filetype": "avro"},
                    }
                ]
            }
            , id="test_convert_with_multiple_path_patterns"
        ),
    ]
)
def test_convert_legacy_config(legacy_config, expected_config):
    parsed_legacy_config = SourceS3Spec(**legacy_config)
    actual_config = LegacyConfigTransformer.convert(parsed_legacy_config)

    assert actual_config == expected_config


@pytest.mark.parametrize(
    "file_type,legacy_format_config,expected_format_config, expected_error",
    [
        pytest.param(
            "csv",
            {
                "filetype": "csv",
                "delimiter": "&",
                "infer_datatypes": False,
                "quote_char": "^",
                "escape_char": "$",
                "encoding": "ansi",
                "double_quote": False,
                "newlines_in_values": True,
                "additional_reader_options": '{"strings_can_be_null": true}',
                "advanced_options": '{"skip_rows": 3, "skip_rows_after_names": 5, "autogenerate_column_names": true}',
                "blocksize": 20000,
            },
            {
                "filetype": "csv",
                "delimiter": "&",
                "quote_char": "^",
                "escape_char": "$",
                "encoding": "ansi",
                "double_quote": False,
                "null_values": ["", "null", "NULL", "N/A", "NA", "NaN", "None"],
                "true_values": ["y", "yes", "t", "true", "on", "1"],
                "false_values": ["n", "no", "f", "false", "off", "0"],
                "inference_type": "None",
                "strings_can_be_null": True,
                "skip_rows_before_header": 3,
                "skip_rows_after_header": 5,
                "autogenerate_column_names": True,
            },
            None,
            id="test_csv_all_legacy_options_set",
        ),
        pytest.param(
            "csv",
            {
                "filetype": "csv",
                "delimiter": "&",
                "quote_char": "^",
                "double_quote": True,
                "newlines_in_values": False,
            },
            {
                "filetype": "csv",
                "delimiter": "&",
                "quote_char": "^",
                "encoding": "utf8",
                "double_quote": True,
                "null_values": ["", "null", "NULL", "N/A", "NA", "NaN", "None"],
                "true_values": ["y", "yes", "t", "true", "on", "1"],
                "false_values": ["n", "no", "f", "false", "off", "0"],
                "inference_type": "Primitive Types Only",
                "strings_can_be_null": False,
            },
            None,
            id="test_csv_only_required_options",
        ),
        pytest.param(
            "csv",
            {},
            {
                "filetype": "csv",
                "delimiter": ",",
                "quote_char": '"',
                "encoding": "utf8",
                "double_quote": True,
                "null_values": ["", "null", "NULL", "N/A", "NA", "NaN", "None"],
                "true_values": ["y", "yes", "t", "true", "on", "1"],
                "false_values": ["n", "no", "f", "false", "off", "0"],
                "inference_type": "Primitive Types Only",
                "strings_can_be_null": False,
            },
            None,
            id="test_csv_empty_format",
        ),
        pytest.param(
            "csv",
            {
                "additional_reader_options": '{"not_valid": "at all}',
            },
            None,
            ValueError,
            id="test_malformed_additional_reader_options",
        ),
        pytest.param(
            "csv",
            {
                "advanced_options": '{"not_valid": "at all}',
            },
            None,
            ValueError,
            id="test_malformed_advanced_options",
        ),
        pytest.param(
            "jsonl",
            {
                "filetype": "jsonl",
                "newlines_in_values": True,
                "unexpected_field_behavior": "ignore",
                "block_size": 0,
            },
            {"filetype": "jsonl"},
            None,
            id="test_jsonl_format",
        ),
        pytest.param(
            "parquet",
            {
                "filetype": "parquet",
                "columns": ["test"],
                "batch_size": 65536,
                "buffer_size": 100,
            },
            {"filetype": "parquet", "decimal_as_float": True},
            None,
            id="test_parquet_format",
        ),
        pytest.param(
            "avro",
            {
                "filetype": "avro",
            },
            {"filetype": "avro"},
            None,
            id="test_avro_format",
        ),
    ],
)
def test_convert_file_format(file_type, legacy_format_config, expected_format_config, expected_error):
    legacy_config = {
        "dataset": "test_data",
        "provider": {
            "storage": "S3",
            "bucket": "test_bucket",
            "aws_access_key_id": "some_access_key",
            "aws_secret_access_key": "some_secret",
        },
        "format": legacy_format_config,
        "path_pattern": f"**/*.{file_type}",
    }

    expected_config = {
        "bucket": "test_bucket",
        "aws_access_key_id": "some_access_key",
        "aws_secret_access_key": "some_secret",
        "streams": [
            {
                "name": "test_data",
                "file_type": file_type,
                "globs": [f"**/*.{file_type}"],
                "legacy_prefix": "",
                "validation_policy": "Emit Record",
                "format": expected_format_config,
            }
        ],
    }

    parsed_legacy_config = SourceS3Spec(**legacy_config)

    if expected_error:
        with pytest.raises(expected_error):
            LegacyConfigTransformer.convert(parsed_legacy_config)
    else:
        actual_config = LegacyConfigTransformer.convert(parsed_legacy_config)
        assert actual_config == expected_config
