#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from dataclasses import dataclass

from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy


@dataclass
class DecalarativeBackoffStrategy(BackoffStrategy, ABC):
    """
    This interface exists to retain backwards compatability with connectors that reference the declarative BackoffStrategy. As part of the effort to promote common interfaces to the Python CDK, this now extends the Python CDK backoff strategy interface.

    Backoff strategy defining how long to wait before retrying a request that resulted in an error.
    """
