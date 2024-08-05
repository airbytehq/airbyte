#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Union

import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.concurrent_source.concurrent_source_adapter import ConcurrentSourceAdapter
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


def _visit_docs_message(logger: logging.Logger, source: ConcurrentSourceAdapter) -> str:
    """
    Creates a message indicating where to look in the documentation for
    more information on a given source by checking the spec of that source
    (if provided) for a 'documentationUrl'.
    :param logger: source logger
    :param source: optional (source)
    :return: A message telling the user where to go to learn more about the source.
    """

    try:
        connector_spec = source.spec(logger)
        docs_url = connector_spec.documentationUrl
        if docs_url:
            return f"Please visit {docs_url} to learn more. "
        else:
            return "Please visit the connector's documentation to learn more. "

    except FileNotFoundError:  # If we are unit testing without implementing spec() method in source
        if source:
            docs_url = f"https://docs.airbyte.com/integrations/sources/{source.name}"
        else:
            docs_url = "https://docs.airbyte.com/integrations/sources/test"

        return f"Please visit {docs_url} to learn more."


class StripeErrorHandler(HttpStatusErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        status_code = response_or_exception.status_code
        if status_code in (requests.codes.bad_request, requests.codes.forbidden):
            parsed_error = response_or_exception.json()
            error_code = parsed_error.get("error", {}).get("code")
            error_message = STRIPE_ERROR_CODES.get(error_code, parsed_error.get("error", {}).get("message"))
            if error_message:
                # todo can I just ifnore the doc message for now?
                # doc_ref = self._visit_docs_message(self._logger, source)
                reason = (
                    f"The endpoint {response_or_exception.url} returned {status_code}: {response_or_exception.reason}. {error_message}."
                )
                # reason = f"The endpoint {response_or_exception.url} returned {status_code}: {response_or_exception.reason}. {error_message}. {doc_ref} "
                response_error_message = HttpStream.parse_response_error_message(response_or_exception)
                if response_error_message:
                    reason += response_error_message

                return ErrorResolution(response_action=ResponseAction.IGNORE, failure_type=FailureType.config_error, error_message=reason)
        return super().interpret_response(response_or_exception)
