#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from abc import ABC
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Tuple, Union, List
from airbyte_cdk.models import SyncMode
import pendulum
import requests
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams import IncrementalMixin

DEFAULT_CAMPAIGN_STATUS = "deleted,active,archived,dirty"


class AudienceprojectStream(HttpStream, ABC):
    url_base = "https://campaign-api.audiencereport.com/"
    oauth_url_base = "https://oauth.audiencereport.com/"

    def __init__(self, config: Mapping[str, Any], authenticator, parent):
        super().__init__(parent)
        self.config = config
        self._authenticator = authenticator
        self._session = requests.sessions.Session()

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(
        self, response: requests.Response, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Mapping]:
        data = response.json().get("data")
        if data:
            data["campaign_id"] = stream_slice["campaign_id"]
            yield data

    @staticmethod
    def _get_time_interval(
            starting_date: Union[pendulum.datetime, str],
            ending_date: Union[pendulum.datetime, str]
    ) -> Iterable[Tuple[pendulum.datetime, pendulum.datetime]]:
        if starting_date:
            if isinstance(starting_date, str):
                starting_date = pendulum.parse(starting_date).date()
        if ending_date:
            ending_date = pendulum.parse(ending_date).date()
            if ending_date < starting_date:
                raise ValueError(
                    f"""Provided start date has to be before end_date.
                        Start date: {starting_date} -> end date: {ending_date}""")
        return starting_date, ending_date

    def stream_slices(
        self, sync_mode: SyncMode.incremental, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent = self.parent(self._authenticator, self.config, **kwargs)
        parent_stream_slices = parent.stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        for stream_slice in parent_stream_slices:
            parent_records = parent.read_records(
                sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=stream_state
            )
            for record in parent_records:
                yield {"campaign_id": record.get("id")}

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return ""


# Basic incremental stream
class IncrementalAudienceprojectStream(AudienceprojectStream, ABC):
    state_checkpoint_interval = None

    @property
    def cursor_field(self) -> str:
        return []

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        return {}


class Campaigns(AudienceprojectStream, ABC):
    primary_key = "id"
    max_records = 100
    start = 0
    parent = ""

    def __init__(self, authenticator, config: Mapping[str, Any], **kwargs):
        super().__init__(config=config, authenticator=authenticator, parent=self.parent)

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        # Start indicates, start index of the campaigns batch with Default value is 0.
        # max_records count of max object in a response indicating total number of campaigns that can be returned.
        # total count indicates total data objects in all pages.
        # All pages are checked even if fetched records are less than total_count that can be fetched.
        total_count = response.json().get("meta").get("totalCount")
        self.start += self.max_records
        record_len = len(response.json().get("data"))
        if record_len < self.max_records or record_len == 0:
            return None
        elif self.start < total_count:
            return {"start": self.start, "maxResults": self.max_records}
        return {"start": self.start, "maxResults": self.max_records}

    def request_params(
            self,
            stream_state: Mapping[str, Any],
            stream_slice: Mapping[str, any] = None,
            next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"type": "all", "sortDirection": "asc"}
        params.update({"status": self.config.get("campaign_status")}) if self.config.get("campaign_status") else params.update(
            {"status": DEFAULT_CAMPAIGN_STATUS})

        start_date = self.config.get("start_date") if self.config.get("start_date") else False
        end_date = self.config.get("end_date") if self.config.get("end_date") else False
        stream_start, stream_end = self._get_time_interval(
            start_date, end_date)
        if stream_end:
            params.update({
                "creationDate": stream_start,
                "reportEnd": stream_end
            })
        if start_date:
            params.update({
                "creationDate": stream_start
            })
        if next_page_token:
            params.update(**next_page_token)
        return params

    @property
    def use_cache(self) -> bool:
        return True

    @property
    def cache_filename(self):
        return "campaigns.yml"

    def stream_slices(
        self, sync_mode: SyncMode.incremental, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None, **kwargs
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield {}

    def parse_response(
        self,
        response: requests.Response,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> Iterable[Mapping]:
        resp = response.json()
        if resp:
            for objects in resp.get("data"):
                objects.update({"created": objects.get("dates").get("created")})
                yield objects

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return "campaigns"


class Devices(AudienceprojectStream, HttpSubStream):

    primary_key = ""
    parent = Campaigns

    def __init__(self, authenticator, config: Mapping[str, Any], **kwargs):
        super().__init__(config=config, authenticator=authenticator, parent=self.parent)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"reports/{stream_slice['campaign_id']}/delivery/devices"


class Profile(AudienceprojectStream, HttpSubStream):

    primary_key = ""
    parent = Campaigns

    def __init__(self, authenticator, config: Mapping[str, Any], **kwargs):
        super().__init__(config=config, authenticator=authenticator, parent=self.parent)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"reports/{stream_slice['campaign_id']}/profile"


class Reach(AudienceprojectStream, HttpSubStream):

    primary_key = ""
    parent = Campaigns

    def __init__(self, authenticator, config: Mapping[str, Any], **kwargs):
        super().__init__(config=config, authenticator=authenticator, parent=self.parent)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"reports/{stream_slice['campaign_id']}/reach"


class Report(AudienceprojectStream, HttpSubStream):

    primary_key = ""
    parent = Campaigns

    def __init__(self, authenticator, config: Mapping[str, Any], **kwargs):
        super().__init__(config=config, authenticator=authenticator, parent=self.parent)

    def path(
        self, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"reports/{stream_slice['campaign_id']}"


