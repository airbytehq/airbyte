#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.file_based.error_handlers.file_based_discover_error_handler import FileBasedDiscoverErrorHandler
from airbyte_cdk.sources.file_based.exceptions import ConfigValidationError, FileBasedSourceError, InvalidSchemaError, SchemaInferenceError

file_based_discover_error_handler = FileBasedDiscoverErrorHandler()


@pytest.mark.parametrize(
    ["exception", "exception_expected"],
    [
        (InvalidSchemaError(FileBasedSourceError.INVALID_SCHEMA_ERROR.value), False),
        (SchemaInferenceError(FileBasedSourceError.SCHEMA_INFERENCE_ERROR.value), False),
        (ConfigValidationError(FileBasedSourceError.CONFIG_VALIDATION_ERROR.value), False),
        (Exception(), True),
    ]

)
def test_handle_discover_error(exception, exception_expected):
    mocked_logger = MagicMock(spec=logging.Logger)

    if exception_expected:
        assert file_based_discover_error_handler.handle_discover_error(mocked_logger, exception) == exception
    else:
        assert file_based_discover_error_handler.handle_discover_error(mocked_logger, exception) is None
        mocked_logger.error.assert_called_with(f"Error occurred while discovering stream and therefore stream will not be added to the configured catalog: {exception}", exc_info=True)
