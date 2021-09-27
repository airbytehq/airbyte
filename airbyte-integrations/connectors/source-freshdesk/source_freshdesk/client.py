#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping, Tuple

from airbyte_protocol import AirbyteStream
from base_python import BaseClient

from .api import (
    API,
    AgentsAPI,
    CompaniesAPI,
    ContactsAPI,
    ConversationsAPI,
    FreshdeskError,
    FreshdeskNotFound,
    FreshdeskUnauthorized,
    GroupsAPI,
    RolesAPI,
    SatisfactionRatingsAPI,
    SkillsAPI,
    SurveysAPI,
    TicketsAPI,
    TimeEntriesAPI,
)


class Client(BaseClient):
    def __init__(self, domain, api_key, requests_per_minute: int = None):
        self._api = API(domain=domain, api_key=api_key, requests_per_minute=requests_per_minute)
        self._apis = {
            "agents": AgentsAPI(self._api),
            "companies": CompaniesAPI(self._api),
            "contacts": ContactsAPI(self._api),
            "conversations": ConversationsAPI(self._api),
            "groups": GroupsAPI(self._api),
            "roles": RolesAPI(self._api),
            "skills": SkillsAPI(self._api),
            "surveys": SurveysAPI(self._api),
            "tickets": TicketsAPI(self._api),
            "time_entries": TimeEntriesAPI(self._api),
            "satisfaction_ratings": SatisfactionRatingsAPI(self._api),
        }
        super().__init__()

    @property
    def streams(self) -> Iterable[AirbyteStream]:
        """List of available streams"""
        for stream in super().streams:
            if stream.source_defined_cursor:
                stream.default_cursor_field = [self._apis[stream.name].state_pk]
            yield stream

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
        except (FreshdeskUnauthorized, FreshdeskNotFound):
            alive = False
            error_msg = "Invalid credentials"
        except FreshdeskError as error:
            alive = False
            error_msg = repr(error)

        return alive, error_msg
