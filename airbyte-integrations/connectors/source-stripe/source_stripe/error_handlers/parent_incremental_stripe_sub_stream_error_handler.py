#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

import requests

from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution
from source_stripe.error_handlers.stripe_error_handler import StripeErrorHandler


class ParentIncrementalStripeSubStreamErrorHandler(StripeErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if not isinstance(response_or_exception, Exception) and response_or_exception.status_code == requests.codes.not_found:
            # When running incremental sync with state, the returned parent object very likely will not contain sub-items
            # as the events API does not support expandable items. Parent class will try getting sub-items from this object,
            # then from its own API. In case there are no sub-items at all for this entity, API will raise 404 error.
            self._logger.warning(
                f"Data was not found for URL: {response_or_exception.request.url}. "
                "If this is a path for getting child attributes like /v1/checkout/sessions/<session_id>/line_items when running "
                "the incremental sync, you may safely ignore this warning."
            )
        return super().interpret_response(response_or_exception)
