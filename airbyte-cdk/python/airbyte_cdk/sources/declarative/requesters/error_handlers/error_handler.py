#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from dataclasses import dataclass

from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler as HttpErrorHandler


@dataclass
class ErrorHandler(HttpErrorHandler, ABC):
    """
    Defines whether a request was successful and how to handle a failure.
    References Python CDK ErrorHandler
    """
