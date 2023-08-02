#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Type

import pytest as pytest
from airbyte_cdk.sources.file_based.config.csv_format import QuotingBehavior
from airbyte_cdk.sources.file_based.config.file_based_stream_config import CsvFormat, FileBasedStreamConfig
from pydantic import ValidationError


@pytest.mark.parametrize(
    "file_type, input_format, expected_format, expected_error",
    [
        pytest.param("csv", {"filetype": "csv", "delimiter": "d", "quote_char": "q", "escape_char": "e", "encoding": "ascii", "double_quote": True, "quoting_behavior": "Quote All"}, {"filetype": "csv", "delimiter": "d", "quote_char": "q", "escape_char": "e", "encoding": "ascii", "double_quote": True, "quoting_behavior": QuotingBehavior.QUOTE_ALL}, None, id="test_valid_format"),
        pytest.param("csv", {"filetype": "csv", "double_quote": False}, {"delimiter": ",", "quote_char": "\"", "encoding": "utf8", "double_quote": False, "quoting_behavior": QuotingBehavior.QUOTE_SPECIAL_CHARACTERS}, None, id="test_default_format_values"),
        pytest.param("csv", {"filetype": "csv", "delimiter": "nope", "double_quote": True}, None, ValidationError, id="test_invalid_delimiter"),
        pytest.param("csv", {"filetype": "csv", "quote_char": "nope", "double_quote": True}, None, ValidationError, id="test_invalid_quote_char"),
        pytest.param("csv", {"filetype": "csv", "escape_char": "nope", "double_quote": True}, None, ValidationError, id="test_invalid_escape_char"),
        pytest.param("csv", {"filetype": "csv", "delimiter": ",", "quote_char": "\"", "encoding": "not_a_format", "double_quote": True}, {}, ValidationError, id="test_invalid_encoding_type"),
        pytest.param("csv", {"filetype": "csv", "double_quote": True, "quoting_behavior": "Quote Invalid"}, None, ValidationError, id="test_invalid_quoting_behavior"),
        pytest.param("invalid", {"filetype": "invalid", "double_quote": False}, {}, ValidationError, id="test_config_format_file_type_mismatch"),
    ]
)
def test_csv_config(file_type: str, input_format: Mapping[str, Any], expected_format: Mapping[str, QuotingBehavior], expected_error: Type[Exception]) -> None:
    stream_config = {
        "name": "stream1",
        "file_type": file_type,
        "globs": ["*"],
        "validation_policy": "emit_record",
        "format": {
            file_type: input_format
        },
    }

    if expected_error:
        with pytest.raises(expected_error):
            FileBasedStreamConfig(**stream_config)
    else:
        actual_config = FileBasedStreamConfig(**stream_config)
        if actual_config.format is not None:
            for expected_format_field, expected_format_value in expected_format.items():
                assert isinstance(actual_config.format[file_type], CsvFormat)
                assert getattr(actual_config.format[file_type], expected_format_field) == expected_format_value
        else:
            assert False, "Expected format to be set"


def test_legacy_format() -> None:
    """
    This test verifies that we can process the legacy format of the config object used by the existing S3 source with a
    single `format` option as opposed to the current file_type -> format mapping.
    """
    stream_config = {
        "name": "stream1",
        "file_type": "csv",
        "globs": ["*"],
        "validation_policy": "emit_record_on_schema_mismatch",
        "format": {
            "filetype": "csv",
            "delimiter": "d",
            "quote_char": "q",
            "escape_char": "e",
            "encoding": "ascii",
            "double_quote": True,
            "quoting_behavior": "Quote All"
        },
    }

    expected_format = {
        "delimiter": "d",
        "quote_char": "q",
        "escape_char": "e",
        "encoding": "ascii",
        "double_quote": True,
        "quoting_behavior": QuotingBehavior.QUOTE_ALL
    }

    actual_config = FileBasedStreamConfig(**stream_config)
    if actual_config.format:
        assert isinstance(actual_config.format["csv"], CsvFormat)
        for expected_format_field, expected_format_value in expected_format.items():
            assert getattr(actual_config.format["csv"], expected_format_field) == expected_format_value
    else:
        assert False, "Expected format to be set"


def test_multiple_file_formats_are_not_supported() -> None:
    formats = {
        "csv": {"filetype": "csv", "delimiter": "d", "quote_char": "q", "escape_char": "e", "encoding": "ascii", "double_quote": True, "quoting_behavior": QuotingBehavior.QUOTE_ALL},
        "parquet": {"filetype": "parquet", "decimal_as_float": True}
    }
    stream_config = {
        "name": "stream1",
        "file_type": "csv",
        "globs": ["*"],
        "validation_policy": "emit_record_on_schema_mismatch",
        "format": formats
    }
    with pytest.raises(ValidationError):
        FileBasedStreamConfig(**stream_config)
