"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, Mapping, Tuple

from base_python import BaseClient

from .api import (
    API,
    AgentsAPI,
    CompaniesAPI,
    ContactsAPI,
    ConversationsAPI,
    FreshdeskError,
    GroupsAPI,
    RolesAPI,
    SatisfactionRatingsAPI,
    SkillsAPI,
    SurveysAPI,
    TicketsAPI,
    TimeEntriesAPI,
)


class Client(BaseClient):
    def __init__(self, domain, api_key):
        self._api = API(domain=domain, api_key=api_key)
        self._apis = {
            "agents": AgentsAPI(self._api),
            "companies": CompaniesAPI(self._api),
            "contacts": ContactsAPI(self._api),
            "conversations": ConversationsAPI(self._api),
            "groups": GroupsAPI(self._api),
            "roles": RolesAPI(self._api),
            "skills": SkillsAPI(self._api),
            "surveys": SurveysAPI(self._api),  # need subscription
            "tickets": TicketsAPI(self._api),
            "time_entries": TimeEntriesAPI(self._api),
            "satisfaction_ratings": SatisfactionRatingsAPI(self._api),
        }
        super().__init__()

    def settings(self):
        url = "settings/helpdesk"
        return self._api.get(url)

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return hasattr(self._apis[name], "state")

    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        return self._apis[name].state

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        self._apis[name].state = state

    def _enumerate_methods(self) -> Mapping[str, callable]:
        return {name: api.list for name, api in self._apis.items()}

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_msg = None

        try:
            self.settings()
        except FreshdeskError as error:
            alive = False
            error_msg = str(error)

        return alive, error_msg
