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
                    "filetype": "csv",
                    "delimiter": "^",
                    "quote_char": "|",
                    "escape_char": "!",
                    "double_quote": True,
                    "quoting_behavior": "Quote All"
                },
                "path_pattern": "**/*.csv",
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
                        "file_type": "csv",
                        "globs": ["a_folder/**/*.csv"],
                        "validation_policy": "Emit Record",
                        "input_schema": '{"col1": "string", "col2": "integer"}',
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
                "path_pattern": "**/*.csv",
            },
            {
                "bucket": "test_bucket",
                "streams": [
                    {
                        "name": "test_data",
                        "file_type": "avro",
                        "globs": ["**/*.csv"],
                        "validation_policy": "Emit Record",
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
