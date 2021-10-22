#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Mapping, Tuple

from base_python import BaseClient
from requests import HTTPError

from .api import (
    ApiTokenAuth,
    OauthTokenAuth,
    AccountOverviewStream,
    AddressesStream,
    AgentsActivityStream,
    AgentsOverviewStream,
    CallLegsStream,
    CallsStream,
    CurrentQueueActivityStream,
    GreetingCategoriesStream,
    GreetingsStream,
    IVRMenusStream,
    IVRRoutesStream,
    IVRsStream,
    PhoneNumbersStream,
)


class ZendeskTalkException(Exception):
    pass


class Client(BaseClient):
    """Zendesk client, provides methods to discover and read streams"""

    def __init__(self, start_date: str, subdomain: str, **kwargs):
        auth_method = kwargs.get("auth_method", {}).get("auth_method")
        if not auth_method or auth_method == "api_token":
            api_token = kwargs["access_token"] if not auth_method else kwargs["auth_method"]["api_token"]
            email = kwargs["email"] if not auth_method else kwargs["auth_method"]["email"]
            self._api = ApiTokenAuth(
                subdomain=subdomain,
                api_token=api_token,
                email=email
            )
        elif auth_method == "access_token":
            access_token = kwargs["auth_method"]["access_token"]
            self._api = OauthTokenAuth(
                subdomain=subdomain,
                access_token=access_token
            )
        else:
            raise ZendeskTalkException(f"incorrect input parameters: {kwargs}")

        self._start_date = start_date
        common_params = dict(api=self._api, start_date=self._start_date)
        self._apis = {
            "phone_numbers": PhoneNumbersStream(**common_params),
            "addresses": AddressesStream(**common_params),
            "greeting_categories": GreetingCategoriesStream(**common_params),
            "greetings": GreetingsStream(**common_params),
            "ivrs": IVRsStream(**common_params),
            "ivr_menus": IVRMenusStream(**common_params),
            "ivr_routes": IVRRoutesStream(**common_params),
            "account_overview": AccountOverviewStream(**common_params),
            "agents_activity": AgentsActivityStream(**common_params),
            "agents_overview": AgentsOverviewStream(**common_params),
            "current_queue_activity": CurrentQueueActivityStream(**common_params),
            "calls": CallsStream(**common_params),
            "call_legs": CallLegsStream(**common_params),
        }

        super().__init__(**kwargs)

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api.list for name, api in self._apis.items()}

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return hasattr(self._apis[name], "state")

    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        return self._apis[name].state

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        self._apis[name].state = state

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            _ = list(self._apis["phone_numbers"].list(fields=[]))
        except HTTPError as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg
