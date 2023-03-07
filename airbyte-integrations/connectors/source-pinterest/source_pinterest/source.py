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

# For Pinterest analytics streams rate limit is 300 calls per day / per user.
# once hit - response would contain `code` property with int.
MAX_RATE_LIMIT_CODE = 8


class PinterestStream(HttpStream, ABC):
    url_base = "https://api.pinterest.com/v5/"
    primary_key = "id"
    data_fields = ["items"]
    raise_on_http_errors = True
    max_rate_limit_exceeded = False

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
        Parsing response data with respect to Rate Limits.
        """
        data = response.json()

        if not self.max_rate_limit_exceeded:
            for data_field in self.data_fields:
                data = data.get(data_field, [])

            for record in data:
                yield record

    def should_retry(self, response: requests.Response) -> bool:
        if isinstance(response.json(), dict):
            self.max_rate_limit_exceeded = response.json().get("code", 0) == MAX_RATE_LIMIT_CODE
        # when max rate limit exceeded, we should skip the stream.
        if response.status_code == requests.codes.too_many_requests and self.max_rate_limit_exceeded:
            self.logger.error(f"For stream {self.name} Max Rate Limit exceeded.")
            setattr(self, "raise_on_http_errors", False)
        return 500 <= response.status_code < 600

    def backoff_time(self, response: requests.Response) -> Optional[float]:
        if response.status_code == requests.codes.too_many_requests:
            self.logger.error(f"For stream {self.name} rate limit exceeded.")
            return float(response.headers.get("X-RateLimit-Reset", 0))


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
    use_cache = True

    def path(self, **kwargs) -> str:
        return "boards"


class AdAccounts(PinterestStream):
    use_cache = True

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
        latest_state = latest_record.get(self.cursor_field, self.start_date.format("YYYY-MM-DD"))
        current_state = current_stream_state.get(self.cursor_field, self.start_date.format("YYYY-MM-DD"))

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

        start_date = self.start_date
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
    def __init__(self, parent: HttpStream, with_data_slices: bool = True, status_filter: str = "", **kwargs):
        super().__init__(parent, with_data_slices, **kwargs)
        self.status_filter = status_filter

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        params = f"?entity_statuses={self.status_filter}" if self.status_filter else ""
        return f"ad_accounts/{stream_slice['parent']['id']}/campaigns{params}"


class CampaignAnalytics(PinterestAnalyticsStream):
    analytics_target_ids = "campaign_ids"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['sub_parent']['parent']['id']}/campaigns/analytics"


class AdGroups(ServerSideFilterStream):
    def __init__(self, parent: HttpStream, with_data_slices: bool = True, status_filter: str = "", **kwargs):
        super().__init__(parent, with_data_slices, **kwargs)
        self.status_filter = status_filter

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        params = f"?entity_statuses={self.status_filter}" if self.status_filter else ""
        return f"ad_accounts/{stream_slice['parent']['id']}/ad_groups{params}"


class AdGroupAnalytics(PinterestAnalyticsStream):
    analytics_target_ids = "ad_group_ids"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['sub_parent']['parent']['id']}/ad_groups/analytics"


class Ads(ServerSideFilterStream):
    def __init__(self, parent: HttpStream, with_data_slices: bool = True, status_filter: str = "", **kwargs):
        super().__init__(parent, with_data_slices, **kwargs)
        self.status_filter = status_filter

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        params = f"?entity_statuses={self.status_filter}" if self.status_filter else ""
        return f"ad_accounts/{stream_slice['parent']['id']}/ads{params}"


class AdAnalytics(PinterestAnalyticsStream):
    analytics_target_ids = "ad_ids"

    def path(self, stream_slice: Mapping[str, Any] = None, **kwargs) -> str:
        return f"ad_accounts/{stream_slice['sub_parent']['parent']['id']}/ads/analytics"


class SourcePinterest(AbstractSource):
    def _validate_and_transform(self, config: Mapping[str, Any]):
        today = pendulum.today()
        AMOUNT_OF_DAYS_ALLOWED_FOR_LOOKUP = 914
        latest_date_allowed_by_api = today.subtract(days=AMOUNT_OF_DAYS_ALLOWED_FOR_LOOKUP)

        start_date = config["start_date"]
        if not start_date:
            config["start_date"] = latest_date_allowed_by_api
        else:
            config["start_date"] = pendulum.from_format(config["start_date"], "YYYY-MM-DD")
            if (today - config["start_date"]).days > AMOUNT_OF_DAYS_ALLOWED_FOR_LOOKUP:
                config["start_date"] = latest_date_allowed_by_api
        return config

    @staticmethod
    def get_authenticator(config):
        config = config.get("credentials") or config
        credentials_base64_encoded = standard_b64encode(
            (config.get("client_id") + ":" + config.get("client_secret")).encode("ascii")
        ).decode("ascii")
        auth = f"Basic {credentials_base64_encoded}"

        return Oauth2Authenticator(
            token_refresh_endpoint=f"{PinterestStream.url_base}oauth/token",
            client_secret=config.get("client_secret"),
            client_id=config.get("client_id"),
            refresh_access_token_headers={"Authorization": auth},
            refresh_token=config.get("refresh_token"),
        )

    def check_connection(self, logger, config) -> Tuple[bool, any]:
        config = self._validate_and_transform(config)
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
        config = self._validate_and_transform(config)
        config["authenticator"] = self.get_authenticator(config)
        status = ",".join(config.get("status")) if config.get("status") else None
        return [
            AdAccountAnalytics(AdAccounts(config), config=config),
            AdAccounts(config),
            AdAnalytics(Ads(AdAccounts(config), with_data_slices=False, config=config), config=config),
            AdGroupAnalytics(AdGroups(AdAccounts(config), with_data_slices=False, config=config), config=config),
            AdGroups(AdAccounts(config), status_filter=status, config=config),
            Ads(AdAccounts(config), status_filter=status, config=config),
            BoardPins(Boards(config), config=config),
            BoardSectionPins(BoardSections(Boards(config), config=config), config=config),
            BoardSections(Boards(config), config=config),
            Boards(config),
            CampaignAnalytics(Campaigns(AdAccounts(config), with_data_slices=False, config=config), config=config),
            Campaigns(AdAccounts(config), status_filter=status, config=config),
            UserAccountAnalytics(None, config=config),
        ]
