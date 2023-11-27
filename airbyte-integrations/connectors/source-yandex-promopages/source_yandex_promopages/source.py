#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
import logging
from abc import ABC
from datetime import datetime, timedelta
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.sources.utils.slice_logger import SliceLogger

from .auth import CredentialsCraftAuthenticator
from .reports_creator import ReportCreator
from .types import Authenticator
from .utils import find_report_candidates

CONFIG_DATE_FORMAT = "%Y-%m-%d"


# Basic full refresh stream
class YandexPromopagesStream(HttpStream, ABC):
    url_base = "https://promopages.yandex.ru/api/promo/v1/"

    def __init__(self, authenticator: Authenticator):
        HttpStream.__init__(self, authenticator=authenticator)


class Publishers(YandexPromopagesStream):
    primary_key = "id"
    use_cache = True

    def path(self, **kwargs) -> str:
        return "permissions/user"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in response.json().get("userPermissions", []):
            yield record["publisher"]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        return {}


class Campaigns(YandexPromopagesStream, HttpSubStream):
    primary_key = "id"
    use_cache = True
    page_limit = 200

    def __init__(self, authenticator: Authenticator, parent: Publishers):
        YandexPromopagesStream.__init__(self, authenticator)
        self.parent = parent

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        data = response.json()
        if data.get("hasNextPage"):
            return {"pageLastId": data.get("pageLastId")}

    def path(self, **kwargs) -> str:
        return "campaigns"

    def request_params(
        self,
        stream_state: Mapping[str, Any] = None,
        stream_slice: Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {"publisherId": stream_slice["parent"]["id"], "pageLimit": self.page_limit}
        if next_page_token:
            params.update(next_page_token)
        return params

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] | None = None,
        next_page_token: Mapping[str, Any] | None = None,
    ) -> Iterable[Mapping]:
        data = response.json()
        for record in data.get("campaigns", []):
            record["publisherId"] = stream_slice["parent"]["id"]
            yield record


class CampaignsStatsReportStream(YandexPromopagesStream, HttpSubStream):
    availability_strategy = None

    def __init__(
        self,
        authenticator: Authenticator,
        date_from: datetime,
        date_to: datetime,
        use_date_chunks: bool,
        date_chunk_period: int,
        parent: Campaigns,
    ):
        HttpSubStream.__init__(self, parent=parent)
        YandexPromopagesStream.__init__(self, authenticator=authenticator)
        self._authenticator = authenticator
        self.date_from = date_from
        self.date_to = date_to
        self.use_date_chunks = use_date_chunks
        self.date_chunk_period = date_chunk_period
        self.parent = parent

    def path(
        self,
        *,
        stream_state: Mapping[str, Any] | None = None,
        stream_slice: Mapping[str, Any] | None = None,
        next_page_token: Mapping[str, Any] | None = None,
    ) -> str:
        return f"reports/{stream_slice['report_id']}"

    def request_params(
        self,
        stream_state: Mapping[str, Any] | None,
        stream_slice: Mapping[str, Any] | None = None,
        next_page_token: Mapping[str, Any] | None = None,
    ) -> MutableMapping[str, Any]:
        return {
            **super().request_params(stream_state, stream_slice, next_page_token),
            "format": "json",
        }

    def next_page_token(self, response: requests.Response) -> Mapping[str, Any] | None:
        return None

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Mapping[str, Any] | None = None,
        next_page_token: Mapping[str, Any] | None = None,
    ) -> Iterable[Mapping[str, Any]]:
        data = response.json()
        for record in data.get("statistics", []):
            yield record

    @property
    def report_endpoint(self) -> str:
        raise NotImplementedError

    def date_slices(self):
        date_chunks = [{"date_from": self.date_from, "date_to": self.date_to}]
        return date_chunks
        # # if not self.use_date_chunks:

        # date_from = self.date_from
        # while date_from < self.date_to:
        #     date_to = date_from + timedelta(days=self.date_chunk_period)
        #     if date_to > self.date_to:
        #         date_to = self.date_to
        #     yield {"date_from": date_from, "date_to": date_to}
        #     date_from = date_to

    def read_full_refresh(
        self,
        cursor_field: Optional[List[str]],
        logger: logging.Logger,
        slice_logger: SliceLogger,
    ) -> Iterable[StreamData]:
        parent_slices = self.stream_slices(
            sync_mode=SyncMode.full_refresh, cursor_field=cursor_field
        )
        logger.debug(
            f"Processing stream slices for {self.name} (sync_mode: full_refresh)",
            extra={"stream_slices": parent_slices},
        )
        report_slices = []
        report_candidates = find_report_candidates(parent_slices)
        report_to_creator_map: dict[str, ReportCreator] = {}
        for report_candidate in report_candidates:
            date_slices = self.date_slices()
            for date_slice in date_slices:
                report_slice = {**report_candidate, **date_slice}
                creator = ReportCreator(
                    publisher_id=report_candidate["publisherId"],
                    campaign_ids=report_candidate["campaignIds"],
                    report_endpoint=self.report_endpoint,
                    msk_date_from=date_slice["date_from"],
                    msk_date_to=date_slice["date_to"],
                    authenticator=self.authenticator,
                )
                report_id = creator.create_report()
                report_to_creator_map[report_id] = creator
                report_slice["report_id"] = report_id
                report_slices.append(report_slice)

        for _slice in report_slices:
            creator = report_to_creator_map[_slice["report_id"]]
            creator.wait_for_report()
            if slice_logger.should_log_slice_message(logger):
                yield slice_logger.create_slice_log_message(_slice)
            yield from self.read_records(
                stream_slice=_slice,
                sync_mode=SyncMode.full_refresh,
                cursor_field=cursor_field,
            )


class CampaignsDailyStats(CampaignsStatsReportStream):
    primary_key = ["campaignId", "mskDate"]
    report_endpoint = "campaigns-daily-stats"


class CampaignsPreviewsDailyStats(CampaignsStatsReportStream):
    primary_key = ["campaignId", "previewId", "mskDate"]
    report_endpoint = "campaigns-previews-daily-stats"


class CampaignsPublicationsDailyStats(CampaignsStatsReportStream):
    primary_key = ["campaignId", "publicationId", "mskDate"]
    report_endpoint = "campaigns-publications-daily-stats"


# Source
class SourceYandexPromopages(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, Any]:
        auth: Authenticator = self.get_auth(config)

        if isinstance(auth, CredentialsCraftAuthenticator):
            success, message = auth.check_connection()
            if not success:
                return False, message

        stream: YandexPromopagesStream = self.streams(config)[0]
        try:
            next(stream.read_records(sync_mode=SyncMode.full_refresh))
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                return False, "Invalid credentials"

        return True, None

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> TokenAuthenticator:
        auth_type = config["credentials"]["auth_type"]
        if auth_type == "access_token_auth":
            return TokenAuthenticator(token=config["credentials"]["access_token"])
        elif auth_type == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                credentials_craft_host=config["credentials"]["credentials_craft_host"],
                credentials_craft_token=config["credentials"]["credentials_craft_token"],
                credentials_craft_token_id=config["credentials"]["credentials_craft_token_id"],
            )
        else:
            raise Exception(
                f"Invalid Auth type {auth_type}. Available: access_token_auth and credentials_craft_auth",
            )

    @staticmethod
    def prepare_config_datetime(config: Mapping[str, Any]) -> Mapping[str, Any]:
        date_range = config["date_range"]
        range_type = config["date_range"]["date_range_type"]
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        prepared_range = {}
        if range_type == "custom_date":
            prepared_range["date_from"] = date_range["date_from"]
            prepared_range["date_to"] = date_range["date_to"]
        elif range_type == "from_date_from_to_today":
            prepared_range["date_from"] = date_range["date_from"]
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        elif range_type == "last_n_days":
            prepared_range["date_from"] = today - timedelta(days=date_range["last_days_count"])
            if date_range["should_load_today"]:
                prepared_range["date_to"] = today
            else:
                prepared_range["date_to"] = today - timedelta(days=1)
        else:
            raise ValueError("Invalid date_range_type")

        if isinstance(prepared_range["date_from"], str):
            prepared_range["date_from"] = datetime.strptime(
                prepared_range["date_from"], CONFIG_DATE_FORMAT
            )

        if isinstance(prepared_range["date_to"], str):
            prepared_range["date_to"] = datetime.strptime(
                prepared_range["date_to"], CONFIG_DATE_FORMAT
            )
        config["prepared_date_range"] = prepared_range
        return config

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        auth = self.get_auth(config)
        config = self.prepare_config_datetime(config)
        publishers_stream = Publishers(authenticator=auth)
        campaigns_stream = Campaigns(authenticator=auth, parent=publishers_stream)
        campaigns_stats_kwargs = dict(
            authenticator=auth,
            date_from=config["prepared_date_range"]["date_from"],
            date_to=config["prepared_date_range"]["date_to"],
            use_date_chunks=False,
            date_chunk_period=1,
            parent=campaigns_stream,
        )
        return [
            publishers_stream,
            campaigns_stream,
            CampaignsDailyStats(**campaigns_stats_kwargs),
            CampaignsPreviewsDailyStats(**campaigns_stats_kwargs),
            CampaignsPublicationsDailyStats(**campaigns_stats_kwargs),
        ]
