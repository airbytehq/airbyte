#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from base64 import standard_b64encode
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import pendulum
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator

from .utils import analytics_columns, to_datetime_str


class PinterestStream(HttpStream, ABC):
    url_base = "https://api.pinterest.com/v5/"
    primary_key = "id"
    data_fields = ["items"]
    raise_on_http_errors = True

    def __init__(self, config: Mapping[str, Any]):
        super().__init__(authenticator=config["authenticator"])
        self.config = config

    @property
    def start_date(self):
        return self.config["start_date"]

    @property
    def window_in_days(self):
        return 30  # Set window_in_days to 30 days date range

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        next_page = response.json().get("bookmark", {}) if self.data_fields else {}

        if next_page:
            return {"bookmark": next_page}

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return next_page_token or {}

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        """
        For Pinterest analytics streams rate limit is 300 calls per day / per user.
        Handling of rate limits for Pinterest analytics streams described in should_retry method of PinterestAnalyticsStream.
        Response example:
            {
                "code": 8,
                "message": "You have exceeded your rate limit. Try again later."
            }
        """

        data = response.json()
        exceeded_rate_limit = False

        if isinstance(data, dict):
            exceeded_rate_limit = data.get("code") == 8

        if not exceeded_rate_limit:
            for data_field in self.data_fields:
                data = data.get(data_field, [])

            for record in data:
                yield record


class PinterestSubStream(HttpSubStream):
    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        parent_stream_slices = self.parent.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field, stream_state=stream_state
        )
        # iterate over all parent stream_slices
        for stream_slice in parent_stream_slices:
            parent_records = self.parent.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)

            # iterate over all parent records with current stream_slice
            for record in parent_records:
                yield {"parent": record, "sub_parent": stream_slice}


class Boards(PinterestStream):
    def path(self, **kwargs) -> str:
        return "boards"


class AdAccounts(PinterestStream):
    def path(self, **kwargs) -> str:
        return "ad_accounts"


class BoardSections(PinterestSubStream, PinterestStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['parent']['id']}/sections"


class BoardPins(PinterestSubStream, PinterestStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['parent']['id']}/pins"


class BoardSectionPins(PinterestSubStream, PinterestStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"boards/{stream_slice['sub_parent']['parent']['id']}/sections/{stream_slice['parent']['id']}/pins"


class IncrementalPinterestStream(PinterestStream, ABC):
    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
        latest_state = latest_record.get(self.cursor_field, self.start_date)
        current_state = current_stream_state.get(self.cursor_field, self.start_date)

        if isinstance(latest_state, int) and isinstance(current_state, str):
            current_state = datetime.strptime(current_state, "%Y-%m-%d").timestamp()

        return {self.cursor_field: max(latest_state, current_state)}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, any]]]:
        """
        Override default stream_slices CDK method to provide date_slices as page chunks for data fetch.
        Returns list of dict, example: [{
            "start_date": "2020-01-01",
            "end_date": "2021-01-02"
            },
            {
            "start_date": "2020-01-03",
            "end_date": "2021-01-04"
            },
            ...]
        """

        start_date = pendulum.parse(self.start_date)
        end_date = pendulum.now()

        # determine stream_state, if no stream_state we use start_date
        if stream_state:
            state = stream_state.get(self.cursor_field)

            state_is_timestamp = isinstance(state, int) or isinstance(state, float)
            if state_is_timestamp:
                state = str(datetime.fromtimestamp(state).date())

            start_date = pendulum.parse(state)

        # use the lowest date between start_date and self.end_date, otherwise API fails if start_date is in future
        start_date = min(start_date, end_date)
        date_slices = []

        while start_date < end_date:
            # the amount of days for each data-chunk begining from start_date
            end_date_slice = start_date.add(days=self.window_in_days)
            date_slices.append({"start_date": to_datetime_str(start_date), "end_date": to_datetime_str(end_date_slice)})

            # add 1 day for start next slice from next day and not duplicate data from previous slice end date.
            start_date = end_date_slice.add(days=1)

        return date_slices


class IncrementalPinterestSubStream(IncrementalPinterestStream):
    cursor_field = "updated_time"

    def __init__(self, parent: HttpStream, with_data_slices: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.parent = parent
        self.with_data_slices = with_data_slices

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        date_slices = super().stream_slices(sync_mode, cursor_field, stream_state) if self.with_data_slices else [{}]
        parents_slices = PinterestSubStream.stream_slices(self, sync_mode, cursor_field, stream_state) if self.parent else [{}]

        for parents_slice in parents_slices:
            for date_slice in date_slices:
                parents_slice.update(date_slice)

                yield parents_slice


class PinterestAnalyticsStream(IncrementalPinterestSubStream):
    primary_key = None
    cursor_field = "DATE"
    data_fields = []
    granularity = "DAY"
    analytics_target_ids = None

    def should_retry(self, response: requests.Response) -> bool:
        if response.status_code == 429:
            self.logger.error(f"For stream {self.name} rate limit exceeded.")
            setattr(self, "raise_on_http_errors", False)
        return 500 <= response.status_code < 600

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update(
            {
                "start_date": stream_slice["start_date"],
                "end_date": stream_slice["end_date"],
                "granularity": self.granularity,
                "columns": analytics_columns,
            }
        )

        if self.analytics_target_ids:
            params.update({self.analytics_target_ids: stream_slice["parent"]["id"]})

        return params


class ServerSideFilterStream(IncrementalPinterestSubStream):
    def filter_by_state(self, stream_state: Mapping[str, Any] = None, record: Mapping[str, Any] = None) -> Iterable:
        """
        Endpoint does not provide query filtering params, but they provide us
        cursor field in most cases, so we used that as incremental filtering
        during the parsing.
        """

        if not stream_state or record[self.cursor_field] >= stream_state.get(self.cursor_field):
            yield record

    def parse_response(self, response: requests.Response, stream_state: Mapping[str, Any], **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, stream_state, **kwargs):
            yield from self.filter_by_state(stream_state=stream_state, record=record)


class UserAccountAnalytics(PinterestAnalyticsStream):
    data_fields = ["all", "daily_metrics"]
    cursor_field = "date"

    def path(self, **kwargs) -> str:
        return "user_account/analytics"


class AdAccountAnalytics(PinterestAnalyticsStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['parent']['id']}/analytics"


class Campaigns(ServerSideFilterStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['parent']['id']}/campaigns"


class CampaignAnalytics(PinterestAnalyticsStream):
    analytics_target_ids = "campaign_ids"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['sub_parent']['parent']['id']}/campaigns/analytics"


class AdGroups(ServerSideFilterStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['parent']['id']}/ad_groups"


class AdGroupAnalytics(PinterestAnalyticsStream):
    analytics_target_ids = "ad_group_ids"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['sub_parent']['parent']['id']}/ad_groups/analytics"


class Ads(ServerSideFilterStream):
    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['parent']['id']}/ads"


class AdAnalytics(PinterestAnalyticsStream):
    analytics_target_ids = "ad_ids"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['sub_parent']['parent']['id']}/ads/analytics"


class SourcePinterest(AbstractSource):
    @staticmethod
    def get_authenticator(config):
        user_pass = (config.get("client_id") + ":" + config.get("client_secret")).encode("ascii")
        auth = "Basic " + standard_b64encode(user_pass).decode("ascii")

        return Oauth2Authenticator(
            token_refresh_endpoint=f"{PinterestStream.url_base}oauth/token",
            client_secret=config.get("client_secret"),
            client_id=config.get("client_id"),
            refresh_access_token_headers={"Authorization": auth},
            refresh_token=config.get("refresh_token"),
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        authenticator = self.get_authenticator(config)
        url = f"{PinterestStream.url_base}user_account"
        auth_headers = {"Accept": "application/json", **authenticator.get_auth_header()}
        try:
            session = requests.get(url, headers=auth_headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        start_date = config.get("start_date")
        if not start_date:
            config["start_date"] = "2020-07-28"  # Set default start_date if user didn't set it

        config["authenticator"] = self.get_authenticator(config)
        return [
            AdAccountAnalytics(AdAccounts(config), config=config),
            AdAccounts(config),
            AdAnalytics(Ads(AdAccounts(config), with_data_slices=False, config=config), config=config),
            AdGroupAnalytics(AdGroups(AdAccounts(config), with_data_slices=False, config=config), config=config),
            AdGroups(AdAccounts(config), config=config),
            Ads(AdAccounts(config), config=config),
            BoardPins(Boards(config), config=config),
            BoardSectionPins(BoardSections(Boards(config), config=config), config=config),
            BoardSections(Boards(config), config=config),
            Boards(config),
            CampaignAnalytics(Campaigns(AdAccounts(config), with_data_slices=False, config=config), config=config),
            Campaigns(AdAccounts(config), config=config),
            UserAccountAnalytics(None, config=config),
        ]
