#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from abc import ABC
from datetime import datetime, timedelta
import json
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple
from airbyte_cdk.models import SyncMode

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from source_jagajam_new.exceptions import ApiError


# Basic full refresh stream
class JagajamNewStream(HttpStream, ABC):
    url_base = "https://app.jagajam.com/v4/"

    def __init__(self, token: str, account_id: str):
        HttpStream.__init__(self, authenticator=None)
        self.token = token
        self.account_id = account_id

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {"token": self.token}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]


class Accounts(JagajamNewStream):
    primary_key = "accountID"

    def path(self, *args, **kwargs) -> str:
        return "accounts"


class Communities(JagajamNewStream):
    primary_key = "communityID"

    def path(self, *args, **kwargs) -> str:
        return f"accounts/{self.account_id}/communities"


# class CommunitiesDetails(JagajamNewStream, HttpSubStream):
#     primary_key = "communityID"

#     def path(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> str:
#         return f"accounts/{self.account_id}/communities/{stream_slice['parent']['communityID']}"


class DateRangeStream(JagajamNewStream, ABC):
    DATE_FORMAT = "%d.%m.%Y"
    DATE_FROM_FIELD_NAME = "from"
    DATE_TO_FIELD_NAME = "to"

    def __init__(
        self,
        token: str,
        account_id: str,
        date_from: datetime,
        date_to: datetime,
        chunks_config: Mapping[str, Any],
    ):
        JagajamNewStream.__init__(
            self,
            token=token,
            account_id=account_id,
        )
        self.date_from = date_from
        self.date_to = date_to
        self.should_split_into_chunks = chunks_config["chunk_mode_type"] == "split_into_chunks"
        self.chunk_size_in_days = chunks_config.get("chunk_size_in_days")

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params.update(
            {
                DateRangeStream.DATE_FROM_FIELD_NAME: datetime.strftime(stream_slice["date_from"], DateRangeStream.DATE_FORMAT),
                DateRangeStream.DATE_TO_FIELD_NAME: datetime.strftime(stream_slice["date_to"], DateRangeStream.DATE_FORMAT),
            }
        )
        return params

    def day_chunks(self, date_from: datetime, date_to: datetime) -> Iterable[datetime]:
        cursor = date_from
        delta = timedelta(days=self.chunk_size_in_days - 1)
        while cursor < date_to:
            if cursor + delta > date_to:
                yield {"date_from": cursor, "date_to": date_to}
                return
            yield {"date_from": cursor, "date_to": cursor + delta}
            cursor = cursor + delta + timedelta(days=1)

    def stream_slices(self, *args, **kwargs) -> Iterable[Optional[Mapping[str, Any]]]:
        if self.should_split_into_chunks:
            day_chunks = list(self.day_chunks(self.date_from, self.date_to))
            yield from day_chunks
        else:
            yield from [{"date_from": self.date_from, "date_to": self.date_to}]


class Posts(DateRangeStream, HttpSubStream):
    primary_key = "postID"

    def __init__(
        self,
        parent: JagajamNewStream,
        token: str,
        account_id: str,
        date_from: datetime,
        date_to: datetime,
        chunks_config: Mapping[str, Any],
    ):
        HttpSubStream.__init__(self, parent=parent)
        DateRangeStream.__init__(self, token, account_id, date_from, date_to, chunks_config)

    def path(self, stream_slice: Mapping[str, Any] = None, *args, **kwargs) -> str:
        return f"accounts/{self.account_id}/communities/{stream_slice['parent']['communityID']}/posts"

    def stream_slices(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for parent_slice in HttpSubStream.stream_slices(self, *args, **kwargs):
            for dates_slice in RetrospectiveStream.stream_slices(self, *args, **kwargs):
                yield {**parent_slice, **dates_slice}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]["posts"]


class RetrospectiveStream(DateRangeStream, ABC):
    primary_key = "date"

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_state, stream_slice, next_page_token)
        params["currentDateFrom"] = params.pop("from")
        params["currentDateTo"] = params.pop("to")
        return params

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        data = response.json()
        for record in data["data"]["series"]:
            yield {**record, "communityID": data["data"]["communityID"]}


class CommunitiesStatistics(RetrospectiveStream, HttpSubStream):
    def __init__(
        self,
        parent: JagajamNewStream,
        token: str,
        account_id: str,
        date_from: datetime,
        date_to: datetime,
        chunks_config: Mapping[str, Any],
    ):
        HttpSubStream.__init__(self, parent=parent)
        RetrospectiveStream.__init__(self, token, account_id, date_from, date_to, chunks_config)

    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"accounts/{self.account_id}/communities/{stream_slice['parent']['communityID']}/statistics/retrospective"

    def stream_slices(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        for parent_slice in HttpSubStream.stream_slices(self, *args, **kwargs):
            for dates_slice in RetrospectiveStream.stream_slices(self, *args, **kwargs):
                yield {**parent_slice, **dates_slice}


class AccountStatisticsRetrospective(RetrospectiveStream):
    def path(
        self, *, stream_state: Mapping[str, Any] = None, stream_slice: Mapping[str, Any] = None, next_page_token: Mapping[str, Any] = None
    ) -> str:
        return f"accounts/{self.account_id}/statistics/summary"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["data"]["series"]


# Source
class SourceJagajamNew(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        test_url = JagajamNewStream.url_base + "check"
        r = requests.get(test_url, params={"token": config["token"]})
        if r.json()["meta"]["code"] != 200:
            return False, json.dumps(r.json())
        available_accounts = self.get_available_accounts(config=config)
        available_accounts_ids = [account["accountID"] for account in available_accounts]
        if config["account_id"] not in available_accounts_ids:
            return False, f"Invalid Account ID. Available: {', '.join(available_accounts_ids)}"

        return True, None

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

    def get_available_accounts(self, config):
        communities_stream_instance = Accounts(token=config["token"], account_id=config["account_id"])
        return list(communities_stream_instance.read_records(sync_mode=SyncMode.full_refresh))

    @staticmethod
    def prepare_config(config: Mapping[str, Any]) -> Mapping[str, Any]:
        config = SourceJagajamNew.transform_config_date_range(config)
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config = SourceJagajamNew.prepare_config(config)
        chunks_config = config.get("chunks", {"chunk_mode_type": "dont_split"})
        shared_kwargs = dict(token=config["token"], account_id=config["account_id"])
        date_range_kwargs = dict(
            date_from=config["date_from_transformed"],
            date_to=config["date_to_transformed"],
            chunks_config=chunks_config,
        )
        communities_stream = Communities(**shared_kwargs)
        return [
            communities_stream,
            Posts(
                parent=communities_stream,
                **shared_kwargs,
                **date_range_kwargs,
            ),
            CommunitiesStatistics(
                parent=communities_stream,
                **shared_kwargs,
                **date_range_kwargs,
            ),
        ]
