#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.exceptions import DefaultBackoffException, UserDefinedBackoffException

DEFAULT_CAMPAIGN_STATUS = "deleted,active,archived,dirty,new"
DEFAULT_END_DATE = pendulum.yesterday().date()
DEFAULT_DATE_FLAG = False


class AudienceprojectStream(HttpStream, ABC):
    url_base = "https://campaign-api.audiencereport.com/"
    oauth_url_base = "https://oauth.audiencereport.com/"
    raise_on_http_errors = True

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
        if response.status_code == 200:
            data = response.json().get("data")
            if data:
                data["campaign_id"] = stream_slice["campaign_id"]
                yield data

    @staticmethod
    def _get_time_interval(
        starting_date: Union[pendulum.datetime, str], ending_date: Union[pendulum.datetime, str]
    ) -> Iterable[Tuple[pendulum.datetime, pendulum.datetime]]:
        if isinstance(starting_date, str):
            start_date = pendulum.parse(starting_date).date()
        if isinstance(ending_date, str):
            end_date = pendulum.parse(ending_date).date()
        else:
            end_date = DEFAULT_END_DATE
        if end_date < start_date:
            raise ValueError(
                f"""Provided start date has to be before end_date.
                     Start date: {start_date} -> end date: {end_date}"""
            )
        return start_date, end_date

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

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 409:
            self.logger.error(f"Skipping stream {self.name}. Full error message: {response.text}")
            setattr(self, "raise_on_http_errors", False)
            return False

    def _send(self, request: requests.PreparedRequest, request_kwargs: Mapping[str, Any]) -> requests.Response:
        self.logger.debug(
            "Making outbound API request", extra={"headers": request.headers, "url": request.url, "request_body": request.body}
        )
        response: requests.Response = self._session.send(request, **request_kwargs)
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug(
                "Receiving response", extra={"headers": response.headers, "status": response.status_code, "body": response.text}
            )
        if self.should_retry(response):
            custom_backoff_time = self.backoff_time(response)
            error_message = self.error_message(response)
            if custom_backoff_time:
                raise UserDefinedBackoffException(
                    backoff=custom_backoff_time, request=request, response=response, error_message=error_message
                )
            else:
                raise DefaultBackoffException(request=request, response=response, error_message=error_message)
        elif self.raise_on_http_errors:
            self.logger.error(response.status_code)
        return response

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
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = {"type": "all", "sortDirection": "asc"}
        params.update({"status": self.config.get("campaign_status")}) if self.config.get("campaign_status") else params.update(
            {"status": DEFAULT_CAMPAIGN_STATUS}
        )
        date_required = self.config.get("date_flag") if self.config.get("date_flag") else DEFAULT_DATE_FLAG
        if date_required:
            stream_start, stream_end = self._get_time_interval(self.config.get("start_date"), self.config.get("end_date"))
            params.update({"creationDate": stream_start, "reportEnd": stream_end})
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
