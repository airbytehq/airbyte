#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
from logging import getLogger
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.streams.http.auth.core import HttpAuthenticator
from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from requests.auth import AuthBase

logger = getLogger("airbyte")


def chunk_range(
    date_from: datetime, date_to: datetime, chunk_size: int
) -> Iterable[Mapping[str, Any]]:
    while date_from <= date_to:
        yield {
            "date_from": date_from,
            "date_to": min(date_from + timedelta(days=chunk_size), date_to),
        }
        date_from += timedelta(days=chunk_size + 1)


# Basic full refresh stream
class AdwileStream(HttpStream, ABC):
    url_base = "https://cabinet.adwile.com/advert/v2/"
    transformer: TypeTransformer = TypeTransformer(
        config=TransformConfig.DefaultSchemaNormalization
    )

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()


class Campaigns(AdwileStream):
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "campaigns"


class DateRangeStream(AdwileStream):
    def __init__(
        self,
        authenticator: HttpAuthenticator = None,
        date_from: datetime = None,
        date_to: datetime = None,
    ):
        super().__init__(authenticator)
        self.date_from = date_from
        self.date_to = date_to

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            **super().request_params(stream_state, stream_slice, next_page_token),
            "date_from": self.date_from.strftime("%Y-%m-%d"),
            "date_to": self.date_to.strftime("%Y-%m-%d"),
        }
        return params


class Stat(DateRangeStream, ABC):
    primary_key = "id"
    group_by = None
    date_granularity = "day"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "stat"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            **super().request_params(stream_state, stream_slice, next_page_token),
            "date_from": stream_slice["date_from"].strftime("%Y-%m-%d"),
            "date_to": stream_slice["date_to"].strftime("%Y-%m-%d"),
            "group_by": [self.group_by, "date"],
            "detail": self.date_granularity,
        }
        logger.info(f"Request params: {params}")
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in response.json()["stat"]:
            for group in record["groups"]:
                yield group

    def stream_slices(
        self,
        *,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        yield from chunk_range(self.date_from, self.date_to, 30)


class CampaignsStat(Stat):
    group_by = "campaign_id"


class SourcesStat(Stat):
    group_by = "source_id"


class TeasersStat(Stat):
    group_by = "teaser_id"


class Teasers(DateRangeStream):
    per_page_records_count = 100000
    primary_key = "id"

    def path(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> str:
        return "teasers"

    def next_page_token(self, response: requests.Response) -> Union[Mapping[str, Any], None]:
        page_info = response.json().get("page_info", {})
        has_next = page_info.get("has_next", True)
        if has_next:
            return {"page": 1000, "per_page": self.per_page_records_count}

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {
            **super().request_params(stream_state, stream_slice, next_page_token),
            "page": next_page_token.get("page", 0) if next_page_token else 0,
        }


# Source
class SourceAdwile(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        test_stream = Campaigns(
            authenticator=self.get_auth(config),
        )
        next(
            test_stream.read_records(
                sync_mode=SyncMode.full_refresh,
            )
        )
        return True, None

    @staticmethod
    def transform_config_date_range(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range: Mapping[str, Any] = config.get("date_range", {})
        date_range_type: str = date_range.get("date_range_type")
        date_from: datetime = None
        date_to: datetime = None
        today_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        from_user_date_format = "%Y-%m-%d"

        if date_range_type == "custom_date":
            date_from = datetime.strptime(date_range.get("date_from"), from_user_date_format)
            date_to = datetime.strptime(date_range.get("date_to"), from_user_date_format)
        elif date_range_type == "from_start_date_to_today":
            date_from = datetime.strptime(date_range.get("date_from"), from_user_date_format)
            if date_range.get("should_load_today"):
                date_to = today_date
            else:
                date_to = today_date - timedelta(days=1)
        elif date_range_type == "last_n_days":
            date_from = today_date - timedelta(date_range.get("last_days_count"))
            if date_range.get("should_load_today"):
                date_to = today_date
            else:
                date_to = today_date - timedelta(days=1)

        config["date_from_transformed"], config["date_to_transformed"] = date_from, date_to
        return config

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> HttpAuthenticator:
        return TokenAuthenticator(token=config["token"], auth_method="Token")

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = self.transform_config_date_range(config)
        auth = self.get_auth(config)
        shared_config = {
            "authenticator": auth,
        }
        date_range_kwargs = {
            "date_from": config["date_from_transformed"],
            "date_to": config["date_to_transformed"],
        }
        return [
            Campaigns(**shared_config),
            Teasers(**shared_config, **date_range_kwargs),
            CampaignsStat(**shared_config, **date_range_kwargs),
            SourcesStat(**shared_config, **date_range_kwargs),
            TeasersStat(**shared_config, **date_range_kwargs),
        ]
