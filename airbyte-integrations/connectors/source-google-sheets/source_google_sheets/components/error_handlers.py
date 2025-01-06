#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Optional, Union

import requests
from requests.status_codes import codes as status_codes

from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import (
    ErrorResolution,
)
from source_google_sheets.batch_size_manager import BatchSizeManager


@dataclass
class SheetDataErrorHandler(DefaultErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        if response_or_exception.status_code == status_codes.TOO_MANY_REQUESTS:
            batch_size_manager = BatchSizeManager()
            batch_size_manager.update_batch_size(batch_size_manager.get_batch_size() + 100)
        return super().interpret_response(response_or_exception)
