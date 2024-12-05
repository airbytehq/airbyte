#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.streams.http.error_handlers.response_models import FailureType, ResponseAction
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from requests import Response
from source_airtable.airtable_error_handler import AirtableErrorHandler
from source_airtable.airtable_error_mapping import AIRTABLE_ERROR_MAPPING
from source_airtable.auth import AirtableOAuth


@pytest.mark.parametrize(
    "auth, json_response, error_message",
    [
        (TokenAuthenticator, {"error": {"type": "INVALID_PERMISSIONS_OR_MODEL_NOT_FOUND"}}, "Personal Access Token does not have required permissions, please add all required permissions to existed one or create new PAT, see docs for more info: https://docs.airbyte.com/integrations/sources/airtable#step-1-set-up-airtable"),
        (AirtableOAuth, {"error": {"type": "INVALID_PERMISSIONS_OR_MODEL_NOT_FOUND"}}, "Access Token does not have required permissions, please reauthenticate."),
        (TokenAuthenticator, {"error": {"type": "Test 403"}}, "Permission denied or entity is unprocessable.")
    ]
)
def test_interpret_response_handles_403_error(auth, json_response, error_message):
    mocked_authenticator = MagicMock(spec=auth)
    mocked_logger = MagicMock(spec=logging.Logger)
    mocked_response = MagicMock(spec=Response)
    mocked_response.status_code = 403
    mocked_response.json.return_value = json_response
    mocked_response.ok = False
    error_handler = AirtableErrorHandler(logger=mocked_logger, authenticator=mocked_authenticator, error_mapping=AIRTABLE_ERROR_MAPPING)
    error_resolution = error_handler.interpret_response(mocked_response)
    assert error_resolution.response_action == ResponseAction.FAIL
    assert error_resolution.failure_type == FailureType.config_error
    assert error_resolution.error_message == error_message

def test_interpret_response_defers_to_airtable_error_mapping_for_other_errors():
    mocked_logger = MagicMock(spec=logging.Logger)
    mocked_response = MagicMock(spec=Response)
    mocked_response.status_code = 404
    mocked_response.ok = False
    error_handler = AirtableErrorHandler(logger=mocked_logger, error_mapping=AIRTABLE_ERROR_MAPPING)
    error_resolution = error_handler.interpret_response(mocked_response)
    assert error_resolution.response_action == AIRTABLE_ERROR_MAPPING[404].response_action
    assert error_resolution.failure_type == AIRTABLE_ERROR_MAPPING[404].failure_type
    assert error_resolution.error_message == AIRTABLE_ERROR_MAPPING[404].error_message
