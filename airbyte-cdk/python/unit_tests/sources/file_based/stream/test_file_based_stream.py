#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest as pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import FileBasedStreamConfig
from pydantic import ValidationError


@pytest.mark.parametrize(
    "input_format, expected_format, expected_error",
    [
        pytest.param({"filetype": "csv", "delimiter": "d", "quote_char": "q", "escape_char": "e", "encoding": "ascii", "double_quote": True, "newlines_in_values": False}, {"delimiter": "d", "quote_char": "q", "escape_char": "e", "encoding": "ascii", "double_quote": True, "newlines_in_values": False}, None, id="test_valid_format"),
        pytest.param({"filetype": "csv", "double_quote": False, "newlines_in_values": True}, {"delimiter": ",", "quote_char": "\"", "encoding": "utf8", "double_quote": False, "newlines_in_values": True}, None, id="test_default_format_values"),
        pytest.param({"filetype": "csv", "delimiter": "nope", "double_quote": True, "newlines_in_values": True}, None, ValidationError, id="test_invalid_delimiter"),
        pytest.param({"filetype": "csv", "quote_char": "nope", "double_quote": True, "newlines_in_values": True}, None, ValidationError, id="test_invalid_quote_char"),
        pytest.param({"filetype": "csv", "escape_char": "nope", "double_quote": True, "newlines_in_values": True}, None, ValidationError, id="test_invalid_escape_char"),
        # we may not need this test, the old code used to replace utf-8 with utf8 but that might not be necessary
        pytest.param({"filetype": "csv", "delimiter": ",", "quote_char": "\"", "encoding": "utf-8", "double_quote": True, "newlines_in_values": True}, {"delimiter": ",", "quote_char": "\"", "encoding": "utf-8", "double_quote": True, "newlines_in_values": True}, None, id="test_replace_utf_8_hyphen"),
        pytest.param({"filetype": "csv", "delimiter": ",", "quote_char": "\"", "encoding": "not_a_format", "double_quote": True, "newlines_in_values": True}, {}, ValidationError, id="test_invalid_encoding_type"),
        pytest.param({"filetype": "jsonl", "double_quote": False, "newlines_in_values": True},
                     {}, ValidationError,
                     id="test_config_format_file_type_mismatch"),
    ]
)
def test_csv_config(input_format, expected_format, expected_error):
    stream_config = {
        "name": "stream1",
        "file_type": "csv",
        "globs": ["*"],
        "validation_policy": "emit_record_on_schema_mismatch",
        "format": input_format,
    }
    if expected_error:
        with pytest.raises(expected_error):
            FileBasedStreamConfig(**stream_config)
    else:
        actual_config = FileBasedStreamConfig(**stream_config)
        for expected_format_field, expected_format_value in expected_format.items():
            assert getattr(actual_config.format, expected_format_field) == expected_format_value
