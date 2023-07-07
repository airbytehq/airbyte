#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.oauth import SingleUseRefreshTokenOauth2Authenticator
from airbyte_cdk.sources.streams.http.requests_native_auth.token import TokenAuthenticator
from requests.auth import AuthBase


# Basic full refresh stream
class SalesloftStream(HttpStream, ABC):

    url_base = "https://api.salesloft.com/v2/"
    datetime_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    primary_key = "id"

    def __init__(self, authenticator: HttpAuthenticator, start_date: str):
        super().__init__(authenticator=authenticator)
        utc_start_date = pendulum.timezone("UTC").convert(pendulum.parse(start_date))
        self.start_date = min(pendulum.now(tz="UTC"), utc_start_date).strftime(self.datetime_format)

    @property
    def created_at_field(self):
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        try:
            if "paging" in response.json()["metadata"].keys():
                next_page = response.json()["metadata"]["paging"].get("next_page")
                return None if not next_page else {"page": next_page}
        except Exception as e:
            raise KeyError(f"error parsing next_page token: {e}")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"per_page": 100, "page": 1}
        if self.created_at_field:
            params[f"{self.created_at_field}[gt]"] = self.start_date
        if next_page_token and "page" in next_page_token:
            params["page"] = next_page_token["page"]
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json().get("data")
        if not data:
            return []
        for element in data:
            yield element


# Basic incremental stream
class IncrementalSalesloftStream(SalesloftStream, ABC):
    @property
    def cursor_field(self) -> str:
        return "updated_at"

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        current_stream_state = current_stream_state or {}

        current_stream_state_date = pendulum.parse(current_stream_state.get(self.cursor_field, self.start_date))
        latest_record_date = pendulum.parse(latest_record.get(self.cursor_field, self.start_date))

        cursor_value = pendulum.timezone("UTC").convert(max(current_stream_state_date, latest_record_date))
        return {self.cursor_field: cursor_value.strftime(self.datetime_format)}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        cursor_value = pendulum.parse(stream_state.get(self.cursor_field, self.start_date))
        cursor_value = min(pendulum.now(tz="UTC"), cursor_value).strftime(self.datetime_format)
        params[f"{self.cursor_field}[gt]"] = cursor_value
        return params


class Users(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "users"


class People(IncrementalSalesloftStream):
    created_at_field = "created_at"

    def path(self, **kwargs) -> str:
        return "people"


class Cadences(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "cadences"


class CadenceMemberships(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "cadence_memberships"


class Emails(IncrementalSalesloftStream):
    created_at_field = "sent_at"

    def path(self, **kwargs) -> str:
        return "activities/emails"


class Calls(IncrementalSalesloftStream):
    created_at_field = "created_at"

    def path(self, **kwargs) -> str:
        return "activities/calls"


class Accounts(IncrementalSalesloftStream):
    created_at_field = "created_at"

    def path(self, **kwargs) -> str:
        return "accounts"


class AccountStages(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "account_stages"


class AccountTiers(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "account_tiers"


class Actions(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "actions"


class EmailTemplates(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "email_templates"


class Import(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "imports"


class Notes(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "notes"


class PersonStages(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "person_stages"


class PhoneNumberAssignments(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "phone_number_assignments"


class Steps(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "steps"


class TeamTemplates(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "team_templates"


class TeamTemplateAttachments(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "team_template_attachments"


class EmailTemplateAttachments(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "email_template_attachments"


class CrmActivities(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "crm_activities"


class Successes(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "successes"


class CrmUsers(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "crm_users"


class Groups(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "groups"


class CustomFields(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "custom_fields"


class CallDataRecords(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "call_data_records"


class CallDispositions(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "call_dispositions"


class CallSentiments(SalesloftStream):
    def path(self, **kwargs) -> str:
        return "call_sentiments"


class Meetings(SalesloftStream):
    created_at_field = "created_at"

    def path(self, **kwargs) -> str:
        return "meetings"


class Searches(IncrementalSalesloftStream):
    created_at_field = "updated_at"

    def path(self, **kwargs) -> str:
        return "meetings/settings/searches"

    @property
    def http_method(self) -> str:
        return "POST"


# Source
class SourceSalesloft(AbstractSource):
    def _create_authenticator(self, config) -> AuthBase:
        if config["credentials"]["auth_type"] == "api_key":
            return TokenAuthenticator(token=config["credentials"]["api_key"])
        return SingleUseRefreshTokenOauth2Authenticator(
            config,
            token_refresh_endpoint="https://accounts.salesloft.com/oauth/token",
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        try:
            auth = self._create_authenticator(config)
            response = requests.get("https://api.salesloft.com/v2/me.json", headers=auth.get_auth_header())
            response.raise_for_status()
            return True, None
        except Exception as e:
            return False, str(e)

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self._create_authenticator(config)
        args = (auth, config["start_date"])
        return [
            Cadences(*args),
            CadenceMemberships(*args),
            People(*args),
            Users(*args),
            Emails(*args),
            Calls(*args),
            AccountStages(*args),
            AccountTiers(*args),
            Accounts(*args),
            Actions(*args),
            EmailTemplates(*args),
            Import(*args),
            Notes(*args),
            PersonStages(*args),
            PhoneNumberAssignments(*args),
            Steps(*args),
            TeamTemplates(*args),
            TeamTemplateAttachments(*args),
            CrmActivities(*args),
            CrmUsers(*args),
            Groups(*args),
            Successes(*args),
            EmailTemplateAttachments(*args),
            CustomFields(*args),
            CallDataRecords(*args),
            CallDispositions(*args),
            CallSentiments(*args),
            Meetings(*args),
            Searches(*args),
        ]
