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
                    "start_date": "2022-01-01T01:02:03Z"

                },
                "format": {
                    "filetype": "avro",
                },
                "path_pattern": "**/*.avro",
                "schema": '{"col1": "string", "col2": "integer"}'
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
                        "globs": ["a_folder/**/*.avro"],
                        "validation_policy": "Emit Record",
                        "input_schema": '{"col1": "string", "col2": "integer"}',
                        "format": {
                            "filetype": "avro"
                        }
                    }
                ]
            }
            , id="test_convert_legacy_config"
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
                        "validation_policy": "Emit Record",
                        "format": {
                            "filetype": "avro"
                        }
                    }
                ]
            }
            , id="test_convert_no_optional_fields"
        ),
    ]
)
def test_convert_legacy_config(legacy_config, expected_config):
    parsed_legacy_config = SourceS3Spec(**legacy_config)
    actual_config = LegacyConfigTransformer.convert(parsed_legacy_config)

    assert actual_config == expected_config


@pytest.mark.parametrize(
    "file_type,legacy_format_config,expected_format_config",
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
            }
            , id="test_csv_all_legacy_options_set"),
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
                "strings_can_be_null": True,
            }
            , id="test_csv_only_required_options"),
        pytest.param(
            "csv",
            {},
            {
                "filetype": "csv",
                "delimiter": ",",
                "quote_char": "\"",
                "encoding": "utf8",
                "double_quote": True,
                "null_values": ["", "null", "NULL", "N/A", "NA", "NaN", "None"],
                "true_values": ["y", "yes", "t", "true", "on", "1"],
                "false_values": ["n", "no", "f", "false", "off", "0"],
                "inference_type": "Primitive Types Only",
                "strings_can_be_null": True,
            }
            , id="test_csv_empty_format"),
        pytest.param(
            "jsonl",
            {
                "filetype": "jsonl",
                "newlines_in_values": True,
                "unexpected_field_behavior": "ignore",
                "block_size": 0,
            },
            {
                "filetype": "jsonl"
            }
            , id="test_jsonl_format"),
        pytest.param(
            "parquet",
            {
                "filetype": "parquet",
                "columns": ["test"],
                "batch_size": 65536,
                "buffer_size": 100,
            },
            {
                "filetype": "parquet"
            }
            , id="test_parquet_format"),
        pytest.param(
            "avro",
            {
                "filetype": "avro",
            },
            {
                "filetype": "avro"
            }
            , id="test_avro_format"),
    ]
)
def test_convert_file_format(file_type, legacy_format_config, expected_format_config):
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
                "validation_policy": "Emit Record",
                "format": expected_format_config
            }
        ]
    }

    parsed_legacy_config = SourceS3Spec(**legacy_config)
    actual_config = LegacyConfigTransformer.convert(parsed_legacy_config)

    assert actual_config == expected_config
