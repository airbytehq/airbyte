#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from abc import ABC, abstractmethod
from typing import Any, Iterable, Mapping, MutableMapping, Optional

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream

from .schemas import Application, BaseSchemaModel, Interview, Note, Offer, Opportunity, Referral, User


class LeverHiringStream(HttpStream, ABC):

    primary_key = "id"
    page_size = 50

    stream_params = {}
    API_VERSION = "v1"

    def __init__(self, base_url: str, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url

    @property
    def url_base(self) -> str:
        return f"{self.base_url}/{self.API_VERSION}/"

    def path(self, **kwargs) -> str:
        return self.name

    @property
    @abstractmethod
    def schema(self) -> BaseSchemaModel:
        """Pydantic model that represents stream schema"""

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        response_data = response.json()
        if response_data.get("hasNext"):
            return {"offset": response_data["next"]}

    def request_params(self, next_page_token: Mapping[str, Any] = None, **kwargs) -> MutableMapping[str, Any]:
        params = {"limit": self.page_size}
        params.update(self.stream_params)
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]

    def get_json_schema(self) -> Mapping[str, Any]:
        """Use Pydantic schema"""
        return self.schema.schema()


class IncrementalLeverHiringStream(LeverHiringStream, ABC):

    state_checkpoint_interval = 100
    cursor_field = "updatedAt"

    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self._start_ts = int(pendulum.parse(start_date).timestamp()) * 1000

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        state_ts = int(current_stream_state.get(self.cursor_field, 0))
        return {self.cursor_field: max(latest_record.get(self.cursor_field), state_ts)}

    def request_params(self, stream_state: Mapping[str, Any] = None, **kwargs):
        stream_state = stream_state or {}
        params = super().request_params(stream_state=stream_state, **kwargs)
        state_ts = int(stream_state.get(self.cursor_field, 0))
        params["updated_at_start"] = max(state_ts, self._start_ts)

        return params


class Opportunities(IncrementalLeverHiringStream):
    """
    Opportunities stream: https://hire.lever.co/developer/documentation#list-all-opportunities
    """

    schema = Opportunity
    base_params = {"include": "followers", "confidentiality": "all"}


class Users(LeverHiringStream):
    """
    Users stream: https://hire.lever.co/developer/documentation#list-all-users
    """

    schema = User
    base_params = {"includeDeactivated": True}


class OpportynityChildStream(LeverHiringStream, ABC):
    def __init__(self, start_date: str, **kwargs):
        super().__init__(**kwargs)
        self._start_date = start_date

    def path(self, stream_slice: Mapping[str, any] = None, **kwargs) -> str:
        return f"opportunities/{stream_slice['opportunity_id']}/{self.name}"

    def stream_slices(self, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        for stream_slice in super().stream_slices(**kwargs):
            opportunities_stream = Opportunities(authenticator=self.authenticator, base_url=self.base_url, start_date=self._start_date)
            for opportunity in opportunities_stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice):
                yield {"opportunity_id": opportunity["id"]}


class Applications(OpportynityChildStream):
    """
    Applications stream: https://hire.lever.co/developer/documentation#list-all-applications
    """

    schema = Application


class Interviews(OpportynityChildStream):
    """
    Interviews stream: https://hire.lever.co/developer/documentation#list-all-interviews
    """

    schema = Interview


class Notes(OpportynityChildStream):
    """
    Notes stream: https://hire.lever.co/developer/documentation#list-all-notes
    """

    schema = Note


class Offers(OpportynityChildStream):
    """
    Offers stream: https://hire.lever.co/developer/documentation#list-all-offers
    """

    schema = Offer


class Referrals(OpportynityChildStream):
    """
    Referrals stream: https://hire.lever.co/developer/documentation#list-all-referrals
    """

    schema = Referral
