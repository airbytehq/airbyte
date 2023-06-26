#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from urllib.parse import parse_qs, urlparse

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream
from requests.auth import AuthBase

from .auth import TrustpilotApikeyAuthenticator


class TrustpilotStream(HttpStream, ABC):
    url_base = "https://api.trustpilot.com/v1/"

    def __init__(self, api_key: str = None, authenticator: AuthBase = None, business_unit_names: List[str] = None):
        super().__init__(authenticator=authenticator)
        self._api_key = api_key
        self._business_unit_names = business_unit_names

    @property
    def data_field(self) -> str:
        """
        Specifies root object name in a stream response

        If not specified, the whole response is passed as a single row.
        """
        return None

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return dict(next_page_token or {})

    def request_headers(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> Mapping[str, Any]:
        return {}

    def _clean_row(self, row: Mapping[str, Any]):
        """
        A internal function to clean the data from API stuff which we do not want to
        store in the stream.
        """
        # We don't want to expose the 'links' in the data
        if "links" in row:
            del row["links"]

        return row

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        json_content = response.json()

        if self.data_field:
            for row in json_content[self.data_field]:
                yield self._clean_row(row)
        else:  # when no data_field is provided, we assume that each request represents
            # a single row.
            yield self._clean_row(json_content)


class TrustpilotPaginagedStream(TrustpilotStream):
    per_page: int = 20
    """
    How many entries shall be get per page. Suggested to use always
    the API max. page size to avoid too many API requests.
    """

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        if self.per_page:
            params["perPage"] = self.per_page
        return params

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        content = response.json()

        # used in e.g. https://documentation-apidocumentation.trustpilot.com/business-units-api-(public)#get-a-list-of-all-business-units
        if "cursor" in content:
            return {"cursor": content["cursor"]}

        # search for a 'next-page' URL in the 'links' part
        # used in e.g. https://documentation-apidocumentation.trustpilot.com/business-units-api#business-unit-private-reviews
        for link in content.get("links", []):
            if link["method"] == "GET" and link["rel"] == "next-page":
                next_page_url = link["href"]
                if next_page_url:
                    next_url = urlparse(next_page_url)
                    return parse_qs(next_url.query)


class TrustpilotIncrementalStream(TrustpilotPaginagedStream, ABC):
    cursor_field = "createdAt"
    filter_param = "startDateTime"
    _start_date: pendulum.DateTime = None

    _current_stream_slice: Mapping[str, any] = None

    def __init__(self, start_date: datetime = None, **kargs):
        super().__init__(**kargs)
        if start_date:
            self._start_date = pendulum.instance(start_date)

    @property
    def state_field(self):
        if "business_unit_id" in self._current_stream_slice:
            return f"{self._current_stream_slice['business_unit_id']}_{self.cursor_field}"
        else:
            return self.cursor_field

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Override to determine the latest state after reading the latest record. This typically compared the cursor_field from the latest record and
        the current state and picks the 'most' recent cursor. This is how a stream's state is determined. Required for incremental.
        """
        latest_state = current_stream_state.get(self.state_field)
        if isinstance(latest_state, str):
            latest_state = pendulum.parse(latest_state)
        last_record_value = pendulum.parse(latest_record[self.cursor_field])
        new_cursor_value = max(last_record_value, latest_state or last_record_value)
        current_stream_state[self.state_field] = str(new_cursor_value)
        return current_stream_state

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        """Add incremental parameters"""
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)

        self._current_stream_slice = stream_slice

        if self.filter_param not in params or self._current_stream_slice != stream_slice:
            # use cursor as filter value only if it is not already a parameter (i.e. we are in the middle of the pagination)
            stream_state = stream_state or {}
            state_str = stream_state.get(self.state_field)
            state = pendulum.parse(state_str) if state_str else self._start_date
            # Note: The Trustpilot API does not specify here the time zone. But
            #       since we take the value from the records, we don't care about
            #       this ...
            params[self.filter_param] = max(state, self._start_date).strftime("%Y-%m-%dT%H:%M:%S")

        return params


class ConfiguredBusinessUnits(TrustpilotStream):
    """
    Iterate over all configured business unit names and returns their public
    information.

    See also: https://documentation-apidocumentation.trustpilot.com/business-units-api-(public)#find-a-business-unit
    """

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "business-units/find"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update({"name": stream_slice["business_unit_name"]})
        return params

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        for business_unit_name in self._business_unit_names:
            yield {"business_unit_name": business_unit_name}


class _AllBusinessUnitsIterator(TrustpilotPaginagedStream):
    """
    Iterates over all available business units and return their minimum data
    including the business unit id which is used further.

    See also https://documentation-apidocumentation.trustpilot.com/business-units-api-(public)#get-a-list-of-all-business-units
    """

    primary_key = "id"
    data_field = "businessUnits"
    per_page = 1000

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "business-units/all"


class BusinessUnits(TrustpilotStream):
    """
    Get the public business information for all business units.

    See also: https://documentation-apidocumentation.trustpilot.com/business-units-api-(public)#get-public-business-unit
    """

    primary_key = "id"

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"business-units/{stream_slice['business_unit_id']}"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        all_business_units = _AllBusinessUnitsIterator(authenticator=self._session.auth)
        for busines_unit_data in all_business_units.read_records(sync_mode=SyncMode.full_refresh):
            yield {"business_unit_id": busines_unit_data["id"]}


class PrivateReviews(TrustpilotIncrementalStream):
    """
    Business Unit private reviews.

    See also: https://documentation-apidocumentation.trustpilot.com/business-units-api#business-unit-private-reviews
    """

    primary_key = "id"
    data_field = "reviews"
    per_page = 100

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"private/business-units/{stream_slice['business_unit_id']}/reviews"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice, next_page_token=next_page_token)
        params.update({"orderBy": "createdat.asc"})
        return params

    def stream_slices(self, stream_state: Mapping[str, Any] = None, **kwargs) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Currently we only support syncing from a specific pre-defined business unit name
        given in the configuration. Probably in a future version when someone demands
        it we could add support for generic business units sync.
        """
        business_units_find = ConfiguredBusinessUnits(
            authenticator=TrustpilotApikeyAuthenticator(token=self._api_key), business_unit_names=self._business_unit_names
        )
        for stream_slice in business_units_find.stream_slices(sync_mode=SyncMode.full_refresh):
            for busines_unit_data in business_units_find.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                yield {"business_unit_id": busines_unit_data["id"]}

    def _clean_row(self, row: Mapping[str, Any]):
        """
        A internal function to clean the data from unnecessary data.
        """
        row = super()._clean_row(row)

        # remove nested 'links'
        if "consumer" in row:
            if "links" in row["consumer"]:
                del row["consumer"]["links"]
        if "businessUnit" in row:
            if "links" in row["businessUnit"]:
                del row["businessUnit"]["links"]

        return row
