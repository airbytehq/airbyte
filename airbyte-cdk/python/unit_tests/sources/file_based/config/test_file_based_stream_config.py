#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping, Type

import pytest as pytest
from airbyte_cdk.sources.file_based.config.file_based_stream_config import CsvFormat, FileBasedStreamConfig
from pydantic.v1.error_wrappers import ValidationError


@pytest.mark.parametrize(
    "file_type, input_format, expected_format, expected_error",
    [
        pytest.param(
            "csv",
            {"filetype": "csv", "delimiter": "d", "quote_char": "q", "escape_char": "e", "encoding": "ascii", "double_quote": True},
            {"filetype": "csv", "delimiter": "d", "quote_char": "q", "escape_char": "e", "encoding": "ascii", "double_quote": True},
            None,
            id="test_valid_format",
        ),
        pytest.param(
            "csv",
            {"filetype": "csv", "double_quote": False},
            {"delimiter": ",", "quote_char": '"', "encoding": "utf8", "double_quote": False},
            None,
            id="test_default_format_values",
        ),
        pytest.param(
            "csv", {"filetype": "csv", "delimiter": "nope", "double_quote": True}, None, ValidationError, id="test_invalid_delimiter"
        ),
        pytest.param(
            "csv", {"filetype": "csv", "quote_char": "nope", "double_quote": True}, None, ValidationError, id="test_invalid_quote_char"
        ),
        pytest.param(
            "csv", {"filetype": "csv", "escape_char": "nope", "double_quote": True}, None, ValidationError, id="test_invalid_escape_char"
        ),
        pytest.param(
            "csv",
            {"filetype": "csv", "delimiter": ",", "quote_char": '"', "encoding": "not_a_format", "double_quote": True},
            {},
            ValidationError,
            id="test_invalid_encoding_type",
        ),
        pytest.param(
            "invalid", {"filetype": "invalid", "double_quote": False}, {}, ValidationError, id="test_config_format_file_type_mismatch"
        ),
    ],
)
def test_csv_config(
    file_type: str, input_format: Mapping[str, Any], expected_format: Mapping[str, Any], expected_error: Type[Exception]
) -> None:
    stream_config = {"name": "stream1", "file_type": file_type, "globs": ["*"], "validation_policy": "Emit Record", "format": input_format}

    if expected_error:
        with pytest.raises(expected_error):
            FileBasedStreamConfig(**stream_config)
    else:
        actual_config = FileBasedStreamConfig(**stream_config)
        if actual_config.format is not None:
            for expected_format_field, expected_format_value in expected_format.items():
                assert isinstance(actual_config.format, CsvFormat)
                assert getattr(actual_config.format, expected_format_field) == expected_format_value
        else:
            assert False, "Expected format to be set"


def test_invalid_validation_policy() -> None:
    stream_config = {
        "name": "stream1",
        "file_type": "csv",
        "globs": ["*"],
        "validation_policy": "Not Valid Policy",
        "format": {
            "filetype": "csv",
            "delimiter": "d",
            "quote_char": "q",
            "escape_char": "e",
            "encoding": "ascii",
            "double_quote": True,
        },
    }
    with pytest.raises(ValidationError):
        FileBasedStreamConfig(**stream_config)
