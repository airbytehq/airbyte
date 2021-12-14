#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import datetime
from enum import Enum
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from urllib.parse import parse_qsl, urlparse

import requests
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.requests_native_auth import TokenAuthenticator
from requests.auth import AuthBase


class IntercomStream(HttpStream, ABC):
    url_base = "https://api.intercom.io/"

    primary_key = "id"
    data_fields = ["data"]

    def __init__(
        self,
        authenticator: AuthBase,
        start_date: str = None,
        **kwargs,
    ):
        self.start_date = start_date

        super().__init__(authenticator=authenticator)

    @property
    def authenticator(self):
        """
        Fix of the bug when isinstance(authenticator, AuthBase) and
        default logic returns  incorrect authenticator values
        """
        if self._session.auth:
            return self._session.auth
        return super().authenticator

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Abstract method of HttpStream - should be overwritten.
        Returning None means there are no more pages to read in response.
        """

        next_page = response.json().get("pages", {}).get("next")

        if next_page:
            return dict(parse_qsl(urlparse(next_page).query))

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {}
        if next_page_token:
            params.update(**next_page_token)
        return params

    def request_headers(self, **kwargs) -> Mapping[str, Any]:
        return {"Accept": "application/json"}

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        try:
            yield from super().read_records(*args, **kwargs)
        except requests.exceptions.HTTPError as e:
            error_message = e.response.text
            if error_message:
                self.logger.error(f"Stream {self.name}: {e.response.status_code} " f"{e.response.reason} - {error_message}")
            raise e

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:

        data = response.json()

        for data_field in self.data_fields:
            if data_field not in data:
                continue
            data = data[data_field]
            if data and isinstance(data, list):
                break

        if isinstance(data, dict):
            yield data
        else:
            yield from data


class IncrementalIntercomStream(IntercomStream, ABC):
    cursor_field = "updated_at"

    def filter_by_state(self, stream_state: Mapping[str, Any] = None, record: Mapping[str, Any] = None) -> Iterable:
        """
        Endpoint does not provide query filtering params, but they provide us
        updated_at field in most cases, so we used that as incremental filtering
        during the slicing.
        """

        if not stream_state or record[self.cursor_field] > stream_state.get(self.cursor_field):
            yield record

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        record = super().parse_response(response, stream_state, **kwargs)

        for record in record:
            yield from self.filter_by_state(stream_state=stream_state, record=record)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, any]:
        """
        This method is called once for each record returned from the API to
        compare the cursor field value in that record with the current state
        we then return an updated state object. If this is the first time we
        run a sync or no state was passed, current_stream_state will be None.
        """

        current_stream_state = current_stream_state or {}

        current_stream_state_date = current_stream_state.get(self.cursor_field, self.start_date)
        latest_record_date = latest_record.get(self.cursor_field, self.start_date)

        return {self.cursor_field: max(current_stream_state_date, latest_record_date)}


class ChildStreamMixin:
    parent_stream_class: Optional[IntercomStream] = None

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        parent_stream = self.parent_stream_class(authenticator=self.authenticator, start_date=self.start_date)
        for slice in parent_stream.stream_slices(sync_mode=sync_mode):
            for item in self.parent_stream_class(
                authenticator=self.authenticator, start_date=self.start_date, stream_slice=slice
            ).read_records(sync_mode=sync_mode):
                yield {"id": item["id"]}


class Admins(IntercomStream):
    """Return list of all admins.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-admins
    Endpoint: https://api.intercom.io/admins
    """

    data_fields = ["admins"]

    def path(self, **kwargs) -> str:
        return "admins"


class Companies(IncrementalIntercomStream):
    """Return list of all companies.
     The Intercom API provides 2 similar endpoint for loading of companies:
    1) "standard" - https://developers.intercom.com/intercom-api-reference/reference#list-companies.
       But this endpoint does not work well for huge datasets and can have performance problems.
    2) "scroll" - https://developers.intercom.com/intercom-api-reference/reference#iterating-over-all-companies
       It has good performance but at same time only one script/client can use it across the client's entire account.

     According to above circumstances no one endpoint can't be used permanently. That's why this stream tries can
    apply both endpoints according to the following logic:
    1) By default the stream tries to load data by "scroll" endpoint.
    2) Try to wait a "scroll" request within a minute (3 attempts with delay 20,5 seconds)
       if a "stroll" is busy by another script
    3) Switch to using of the "standard" endpoint.
    """

    class EndpointType(Enum):
        scroll = "companies/scroll"
        standard = "companies"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._backoff_count = 0
        self._endpoint_type = self.EndpointType.scroll
        self._total_count = None  # uses for saving of a total_count value once

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """For reset scroll needs to iterate pages untill the last.
        Another way need wait 1 min for the scroll to expire to get a new list for companies segments."""
        data = response.json()
        if self._total_count is None and data.get("total_count"):
            self._total_count = data["total_count"]
            self.logger.info(f"found {self._total_count} companies")
        if self.can_use_scroll():

            scroll_param = data.get("scroll_param")

            # this stream always has only one data field
            data_field = self.data_fields[0]
            if scroll_param and data.get(data_field):
                return {"scroll_param": scroll_param}
        elif not data.get("errors"):
            return super().next_page_token(response)
        return None

    def can_use_scroll(self):
        """Check backoff count"""
        return self._backoff_count <= 3

    def path(self, **kwargs) -> str:
        return self._endpoint_type.value

    @classmethod
    def check_exists_scroll(cls, response: requests.Response) -> bool:
        if response.status_code == 400:
            # example response:
            # {..., "errors": [{'code': 'scroll_exists', 'message': 'scroll already exists for this workspace'}]}
            err_body = response.json()["errors"][0]
            if err_body["code"] == "scroll_exists":
                return True

        return False

    @property
    def raise_on_http_errors(self) -> bool:
        if not self.can_use_scroll() and self._endpoint_type == self.EndpointType.scroll:
            return False
        return True

    def stream_slices(self, sync_mode, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        yield None
        if not self.can_use_scroll():
            self._endpoint_type = self.EndpointType.standard
            yield None

    def should_retry(self, response: requests.Response) -> bool:
        if self.check_exists_scroll(response):
            self._backoff_count += 1
            if not self.can_use_scroll():
                self.logger.error("Can't create a new scroll request within an minute. " "Let's try to use a standard non-scroll endpoint.")
                return False

            return True
        return super().should_retry(response)

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if self.check_exists_scroll(response):
            self.logger.warning("A previous scroll request is exists. " "It must be deleted within an minute automatically")
            # try to check 3 times
            return 20.5
        return super().backoff_time(response)

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        if not self.raise_on_http_errors:
            data = response.json()
            if data.get("errors"):
                return
        yield from super().parse_response(response, stream_state=stream_state, **kwargs)


class CompanySegments(ChildStreamMixin, IncrementalIntercomStream):
    """Return list of all company segments.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-attached-segments-1
    Endpoint: https://api.intercom.io/companies/<id>/segments
    """

    parent_stream_class = Companies

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"/companies/{stream_slice['id']}/segments"


class Conversations(IncrementalIntercomStream):
    """Return list of all conversations.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-conversations
    Endpoint: https://api.intercom.io/conversations
    """

    data_fields = ["conversations"]

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(next_page_token, **kwargs)
        params.update({"order": "asc", "sort": self.cursor_field})
        return params

    def path(self, **kwargs) -> str:
        return "conversations"


class ConversationParts(ChildStreamMixin, IncrementalIntercomStream):
    """Return list of all conversation parts.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#retrieve-a-conversation
    Endpoint: https://api.intercom.io/conversations/<id>
    """

    data_fields = ["conversation_parts", "conversation_parts"]
    parent_stream_class = Conversations

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"/conversations/{stream_slice['id']}"


class Segments(IncrementalIntercomStream):
    """Return list of all segments.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-segments
    Endpoint: https://api.intercom.io/segments
    """

    data_fields = ["segments"]

    def path(self, **kwargs) -> str:
        return "segments"


class Contacts(IncrementalIntercomStream):
    """Return list of all contacts.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-contacts
    Endpoint: https://api.intercom.io/contacts
    """

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        """
        Abstract method of HttpStream - should be overwritten.
        Returning None means there are no more pages to read in response.
        """

        next_page = response.json().get("pages", {}).get("next")

        if isinstance(next_page, dict):
            return {"starting_after": next_page["starting_after"]}

        if isinstance(next_page, str):
            return super().next_page_token(response)

    def path(self, **kwargs) -> str:
        return "contacts"


class DataAttributes(IntercomStream):
    primary_key = "name"

    def path(self, **kwargs) -> str:
        return "data_attributes"


class CompanyAttributes(DataAttributes):
    """Return list of all data attributes belonging to a workspace for companies.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-data-attributes
    Endpoint: https://api.intercom.io/data_attributes?model=company
    """

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"model": "company"}


class ContactAttributes(DataAttributes):
    """Return list of all data attributes belonging to a workspace for contacts.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-data-attributes
    Endpoint: https://api.intercom.io/data_attributes?model=contact
    """

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        return {"model": "contact"}


class Tags(IntercomStream):
    """Return list of all tags.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-tags-for-an-app
    Endpoint: https://api.intercom.io/tags
    """

    primary_key = "name"

    def path(self, **kwargs) -> str:
        return "tags"


class Teams(IntercomStream):
    """Return list of all teams.
    API Docs: https://developers.intercom.com/intercom-api-reference/reference#list-teams
    Endpoint: https://api.intercom.io/teams
    """

    primary_key = "name"
    data_fields = ["teams"]

    def path(self, **kwargs) -> str:
        return "teams"


class VersionApiAuthenticator(TokenAuthenticator):
    """Intercom API support its dynamic versions' switching.
    But this connector should support only one for any resource account and
    it is realised by the additional request header 'Intercom-Version'
    Docs: https://developers.intercom.com/building-apps/docs/update-your-api-version#section-selecting-the-version-via-the-developer-hub
    """

    relevant_supported_version = "2.2"

    def get_auth_header(self) -> Mapping[str, Any]:
        headers = super().get_auth_header()
        headers["Intercom-Version"] = self.relevant_supported_version
        return headers


class SourceIntercom(AbstractSource):
    """
    Source Intercom fetch data from messaging platform.
    """

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        authenticator = VersionApiAuthenticator(token=config["access_token"])
        try:
            url = f"{IntercomStream.url_base}/tags"
            auth_headers = {"Accept": "application/json", **authenticator.get_auth_header()}
            session = requests.get(url, headers=auth_headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["start_date"] = datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%SZ").timestamp()
        AirbyteLogger().log("INFO", f"Using start_date: {config['start_date']}")

        auth = VersionApiAuthenticator(token=config["access_token"])
        return [
            Admins(authenticator=auth, **config),
            Companies(authenticator=auth, **config),
            CompanySegments(authenticator=auth, **config),
            Conversations(authenticator=auth, **config),
            ConversationParts(authenticator=auth, **config),
            Contacts(authenticator=auth, **config),
            CompanyAttributes(authenticator=auth, **config),
            ContactAttributes(authenticator=auth, **config),
            Segments(authenticator=auth, **config),
            Tags(authenticator=auth, **config),
            Teams(authenticator=auth, **config),
        ]
