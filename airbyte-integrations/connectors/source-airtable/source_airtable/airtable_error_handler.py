#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from datetime import timedelta
from typing import Mapping, Optional, Union

import requests
from airbyte_cdk.sources.streams.http.error_handlers import HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, FailureType, ResponseAction
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from source_airtable.airtable_error_mapping import AIRTABLE_ERROR_MAPPING
from source_airtable.auth import AirtableOAuth


class AirtableErrorHandler(HttpStatusErrorHandler):
    def __init__(
        self,
        logger: logging.Logger,
        error_mapping: Optional[Mapping[Union[int, str, type[Exception]], ErrorResolution]] = AIRTABLE_ERROR_MAPPING,
        max_retries: int = 5,
        max_time: timedelta = timedelta(seconds=600),
        authenticator: Optional[Union[TokenAuthenticator, AirtableOAuth]] = None,
    ) -> None:
        self._authenticator = authenticator
        self.logger = logger
        super().__init__(self.logger, error_mapping, max_retries, max_time)

    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if (
            isinstance(response_or_exception, requests.Response)
            and response_or_exception.status_code == 403
            and response_or_exception.json().get("error", {}).get("type") == "INVALID_PERMISSIONS_OR_MODEL_NOT_FOUND"
        ):
            if isinstance(self._authenticator, TokenAuthenticator):
                error_message = "Personal Access Token does not have required permissions, please add all required permissions to existed one or create new PAT, see docs for more info: https://docs.airbyte.com/integrations/sources/airtable#step-1-set-up-airtable"
            else:
                error_message = "Access Token does not have required permissions, please reauthenticate."

            return ErrorResolution(response_action=ResponseAction.FAIL, failure_type=FailureType.config_error, error_message=error_message)
        else:
            return super().interpret_response(response_or_exception)
