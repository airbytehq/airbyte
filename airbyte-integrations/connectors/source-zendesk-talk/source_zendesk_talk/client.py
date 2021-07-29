#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from typing import Any, Mapping, Tuple

from base_python import BaseClient
from requests import HTTPError

from .api import (
    API,
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


class Client(BaseClient):
    """Zendesk client, provides methods to discover and read streams"""

    def __init__(self, start_date: str, subdomain: str, access_token: str, email: str, **kwargs):
        self._start_date = start_date
        self._api = API(subdomain=subdomain, access_token=access_token, email=email)

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
