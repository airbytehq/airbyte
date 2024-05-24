#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC

from airbyte_cdk.sources.streams.http.error_handlers import BackoffStrategy as HttpBackoffStrategy


class BackoffStrategy(HttpBackoffStrategy, ABC):
    """
    Backoff strategy defining how long to wait before retrying a request that resulted in an error.
    References Python CDK BackoffStrategy
    """
