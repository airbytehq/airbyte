# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Dict, Mapping

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import (
    NoAuth,
)
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import (
    InterpolatedString,
)
from airbyte_cdk.sources.declarative.requesters import HttpRequester
from airbyte_cdk.sources.declarative.requesters.request_options.interpolated_request_options_provider import (
    InterpolatedRequestOptionsProvider,
)
from airbyte_cdk.sources.declarative.requesters.requester import HttpMethod
from airbyte_cdk.sources.streams.call_rate import (
    APIBudget,
    HttpRequestMatcher,
    LimiterMixin,
    MovingWindowCallRatePolicy,
    Rate,
    UnlimitedCallRatePolicy,
)
from airbyte_cdk.sources.streams.http import HttpClient
from airbyte_cdk.sources.types import EmptyString


MESSAGES_AND_THREADS_RATE = Rate(limit=1, interval=timedelta(seconds=60))


class MessagesAndThreadsApiBudget(APIBudget, LimiterMixin):
    """
    Switches to MovingWindowCallRatePolicy 1 request per minute if rate limits were exceeded.
    """

    def update_from_response(self, request: Any, response: Any) -> None:
        current_policy = self.get_matching_policy(request)
        if response.status_code == 429 and isinstance(current_policy, UnlimitedCallRatePolicy):
            matchers = current_policy._matchers
            self._policies = [
                MovingWindowCallRatePolicy(
                    matchers=matchers,
                    rates=[MESSAGES_AND_THREADS_RATE],
                )
            ]


@dataclass
class MessagesAndThreadsHttpRequester(HttpRequester):
    """
    Redefines Custom API Budget to handle rate limits.
    """

    url_match: str = None
    # redefine this here to set up in InterpolatedRequestOptionsProvider in __post_init__
    request_parameters: Dict[str, Any] = None

    def __post_init__(self, parameters: Mapping[str, Any]) -> None:
        self._url = InterpolatedString.create(self.url if self.url else EmptyString, parameters=parameters)
        # deprecated
        self._url_base = InterpolatedString.create(self.url_base if self.url_base else EmptyString, parameters=parameters)
        # deprecated
        self._path = InterpolatedString.create(self.path if self.path else EmptyString, parameters=parameters)
        if self.request_options_provider is None:
            self._request_options_provider = InterpolatedRequestOptionsProvider(
                config=self.config,
                parameters=parameters,
                request_parameters=self.request_parameters,
            )
        elif isinstance(self.request_options_provider, dict):
            self._request_options_provider = InterpolatedRequestOptionsProvider(config=self.config, **self.request_options_provider)
        else:
            self._request_options_provider = self.request_options_provider
        self._authenticator = self.authenticator or NoAuth(parameters=parameters)
        self._http_method = HttpMethod[self.http_method] if isinstance(self.http_method, str) else self.http_method
        self.error_handler = self.error_handler
        self._parameters = parameters

        if self.error_handler is not None and hasattr(self.error_handler, "backoff_strategies"):
            backoff_strategies = self.error_handler.backoff_strategies  # type: ignore
        else:
            backoff_strategies = None

        self._http_client = HttpClient(
            name=self.name,
            logger=self.logger,
            error_handler=self.error_handler,
            api_budget=MessagesAndThreadsApiBudget(
                policies=[
                    UnlimitedCallRatePolicy(
                        matchers=[HttpRequestMatcher(url=self.url_match)],
                    )
                ]
            ),
            authenticator=self._authenticator,
            use_cache=self.use_cache,
            backoff_strategy=backoff_strategies,
            disable_retries=self.disable_retries,
            message_repository=self.message_repository,
        )
