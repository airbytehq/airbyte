#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Optional, Union

from requests import Response

from airbyte_cdk.sources.streams.http.error_handlers import HttpStatusErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import ErrorResolution, FailureType, ResponseAction


class RechargeErrorHandler(HttpStatusErrorHandler):
    def __init__(self, logger: logging.Logger) -> None:
        self.logger = logger
        super().__init__(logger=logger)

    def interpret_response(self, response_or_exception: Optional[Union[Response, Exception]] = None) -> ErrorResolution:
        if isinstance(response_or_exception, Response):
            content_length = int(response_or_exception.headers.get("Content-Length", 0))
            incomplete_data_response = response_or_exception.status_code == 200 and content_length > len(response_or_exception.content)
            if incomplete_data_response:
                return ErrorResolution(
                    response_action=ResponseAction.RETRY,
                    failure_type=FailureType.transient_error,
                    error_message="The response is incomplete, retrying the request.",
                )

        return super().interpret_response(response_or_exception)
