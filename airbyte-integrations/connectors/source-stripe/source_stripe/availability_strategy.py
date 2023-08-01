#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Tuple

from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from requests import HTTPError

STRIPE_ERROR_CODES = {
    "more_permissions_required": "This is most likely due to insufficient permissions on the credentials in use. "
    "Try to grant required permissions/scopes or re-authenticate",
    "account_invalid": "The card, or account the card is connected to, is invalid. You need to contact your card issuer "
    "to check that the card is working correctly.",
    "oauth_not_supported": "Please use a different authentication method.",
}


class StripeAvailabilityStrategy(HttpAvailabilityStrategy):
    def handle_http_error(
        self, stream: Stream, logger: logging.Logger, source: Optional["Source"], error: HTTPError
    ) -> Tuple[bool, Optional[str]]:
        status_code = error.response.status_code
        if status_code not in [400, 403]:
            raise error
        parsed_error = error.response.json()
        error_code = parsed_error.get("error", {}).get("code")
        error_message = STRIPE_ERROR_CODES.get(error_code, parsed_error.get("error", {}).get("message"))
        if not error_message:
            raise error
        doc_ref = self._visit_docs_message(logger, source)
        reason = f"The endpoint {error.response.url} returned {status_code}: {error.response.reason}. {error_message}. {doc_ref} "
        response_error_message = stream.parse_response_error_message(error.response)
        if response_error_message:
            reason += response_error_message
        return False, reason


class StripeSubStreamAvailabilityStrategy(HttpAvailabilityStrategy):
    def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional[Source]) -> Tuple[bool, Optional[str]]:
        """Traverse through all the parents of a given stream and run availability strategy on each of them"""
        try:
            current_stream, parent_stream = stream, getattr(stream, "parent")
        except AttributeError:
            return super().check_availability(stream, logger, source)
        if parent_stream:
            parent_stream_instance = getattr(current_stream, "get_parent_stream_instance")()
            # Accessing the `availability_strategy` property will instantiate AvailabilityStrategy under the hood
            availability_strategy = parent_stream_instance.availability_strategy
            if availability_strategy:
                is_available, reason = availability_strategy.check_availability(parent_stream_instance, logger, source)
                if not is_available:
                    return is_available, reason
        return super().check_availability(stream, logger, source)
