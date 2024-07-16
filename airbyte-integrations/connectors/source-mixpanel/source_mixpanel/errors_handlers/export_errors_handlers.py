#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Optional, Union

import requests
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.error_handlers import ErrorResolution, HttpStatusErrorHandler, ResponseAction
from airbyte_protocol.models import FailureType

from .base_errors_handlers import DateSlicesMixinErrorHandler, MixpanelStreamErrorHandler


class ExportErrorHandler(MixpanelStreamErrorHandler, DateSlicesMixinErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, requests.Response):
            try:
                # trying to parse response to avoid ConnectionResetError and retry if it occurs
                self.stream.iter_dicts(response_or_exception.iter_lines(decode_unicode=True))
            except ConnectionResetError:
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message=f"Response status code: {response_or_exception.status_code}. Retrying...",  # type: ignore[union-attr]
                )
        return super().interpret_response(response_or_exception)
