#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Optional

import aiohttp
import aiohttp_client_cache

from airbyte_cdk.sources.streams.call_rate import AbstractAPIBudget

MIXIN_BASE = aiohttp.ClientSession

logger = logging.getLogger("airbyte")


class AsyncLimiterMixin(MIXIN_BASE):
    """Mixin class that adds rate-limiting behavior to requests."""

    def __init__(
        self,
        api_budget: Optional[AbstractAPIBudget],
        **kwargs: Any,
    ):
        self._api_budget = api_budget
        super().__init__(**kwargs)  # type: ignore # Base Session doesn't take any kwargs

    async def send(
        self, request: aiohttp.ClientRequest, **kwargs: Any
    ) -> aiohttp.ClientResponse:
        """Send a request with rate-limiting."""
        assert (
            self._api_budget is None
        ), "API budgets are not supported in the async CDK yet."
        return await super().send(request, **kwargs)  # type: ignore # MIXIN_BASE should be used with aiohttp.ClientSession


class AsyncLimiterSession(AsyncLimiterMixin, aiohttp.ClientSession):
    """Session that adds rate-limiting behavior to requests."""


class AsyncCachedLimiterSession(
    aiohttp_client_cache.CachedSession, AsyncLimiterMixin, aiohttp.ClientSession
):
    """Session class with caching and rate-limiting behavior."""
