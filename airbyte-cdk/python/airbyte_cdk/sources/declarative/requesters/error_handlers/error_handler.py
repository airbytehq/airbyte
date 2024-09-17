#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from dataclasses import dataclass

from airbyte_cdk.sources.streams.http.error_handlers import ErrorHandler


@dataclass
class DeclarativeErrorHandler(ErrorHandler, ABC):
    """
    This interface exists to retain backwards compatability with connectors that reference the declarative ErrorHandler. As part of the effort to promote common interfaces to the Python CDK, this now extends the Python CDK ErrorHandler interface.

    `ErrorHandler` defines how to handle errors that occur during the request process, returning an ErrorResolution object that defines how to proceed.
    """
