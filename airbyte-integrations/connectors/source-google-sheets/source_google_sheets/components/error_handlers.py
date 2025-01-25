#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass
from typing import Optional, Union

import requests

from airbyte_cdk.sources.declarative.requesters.error_handlers.default_error_handler import DefaultErrorHandler
from airbyte_cdk.sources.streams.http.error_handlers.response_models import (
    ErrorResolution,
)
from source_google_sheets.batch_size_manager import BatchSizeManager


@dataclass
class SheetDataErrorHandler(DefaultErrorHandler):
    def interpret_response(self, response_or_exception: Optional[Union[requests.Response, Exception]]) -> ErrorResolution:
        BatchSizeManager().increase_row_batch_size(response_or_exception)
        return super().interpret_response(response_or_exception)
