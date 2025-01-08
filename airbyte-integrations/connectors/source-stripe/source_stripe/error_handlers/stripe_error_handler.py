#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Union

import requests

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, ResponseAction


STRIPE_ERROR_CODES = {
    "more_permissions_required": "This is most likely due to insufficient permissions on the credentials in use. "
    "Try to grant required permissions/scopes or re-authenticate",
    "account_invalid": "The card, or account the card is connected to, is invalid. You need to contact your card issuer "
    "to check that the card is working correctly.",
    "oauth_not_supported": "Please use a different authentication method.",
}

DOCS_URL = f"https://docs.airbyte.com/integrations/sources/stripe"
DOCUMENTATION_MESSAGE = f"Please visit {DOCS_URL} to learn more. "


class StripeErrorHandler(HttpStatusErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if not isinstance(response_or_exception, Exception) and response_or_exception.status_code in (
            requests.codes.bad_request,
            requests.codes.forbidden,
        ):
            parsed_error = response_or_exception.json()
            error_code = parsed_error.get("error", {}).get("code")
            error_message = STRIPE_ERROR_CODES.get(error_code, parsed_error.get("error", {}).get("message"))
            if error_message:
                reason = f"The endpoint {response_or_exception.url} returned {response_or_exception.status_code}: {response_or_exception.reason}. {error_message}.  {DOCUMENTATION_MESSAGE} "
                response_error_message = HttpStream.parse_response_error_message(response_or_exception)
                if response_error_message:
                    reason += response_error_message

                return ErrorResolution(response_action=ResponseAction.IGNORE, error_message=reason)
        return super().interpret_response(response_or_exception)
