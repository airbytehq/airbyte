#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import abc
import datetime
import logging
from typing import TYPE_CHECKING, Any

import aiohttp
import aiohttp_client_cache

from airbyte_cdk.sources.streams.call_rate import AbstractAPIBudget

# prevents mypy from complaining about missing session attributes in LimiterMixin
if TYPE_CHECKING:
    MIXIN_BASE = aiohttp.ClientSession
else:
    MIXIN_BASE = object

logger = logging.getLogger("airbyte")


class AsyncLimiterMixin(MIXIN_BASE):
    """Mixin class that adds rate-limiting behavior to requests."""

    def __init__(
        self,
        api_budget: AbstractAPIBudget,
        **kwargs: Any,
    ):
        self._api_budget = api_budget
        super().__init__(**kwargs)  # type: ignore # Base Session doesn't take any kwargs

    async def send(self, request: aiohttp.ClientRequest, **kwargs: Any) -> aiohttp.ClientResponse:
        """Send a request with rate-limiting."""
        self._api_budget.acquire_call(request)
        response = await super().send(request, **kwargs)
        self._api_budget.update_from_response(request, response)
        return response


class AsyncLimiterSession(AsyncLimiterMixin, aiohttp.ClientSession):
    """Session that adds rate-limiting behavior to requests."""


class AsyncCachedLimiterSession(aiohttp_client_cache.CachedSession, AsyncLimiterMixin, aiohttp.ClientSession):
    """Session class with caching and rate-limiting behavior."""
