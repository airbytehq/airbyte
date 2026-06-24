#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import json
import logging
import os
import re
from dataclasses import InitVar, dataclass
from typing import Any, ClassVar, Iterable, Mapping, Optional, Union

import requests

from airbyte_cdk.sources.declarative.auth.declarative_authenticator import DeclarativeAuthenticator
from airbyte_cdk.sources.declarative.interpolation.interpolated_string import InterpolatedString
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor
from airbyte_cdk.sources.declarative.requesters.http_requester import HttpRequester
from airbyte_cdk.sources.declarative.types import Config
from airbyte_cdk.sources.types import StreamSlice, StreamState

BUSINESS_USER_FIELDS = [
    "address_clicks",
    "app_download_clicks",
    "audience_activity",
    "audience_ages",
    "audience_cities",
    "audience_countries",
    "audience_genders",
    "average_comments",
    "average_likes",
    "average_shares",
    "average_views",
    "bio_description",
    "bio_link_clicks",
    "comments",
    "completion_rate",
    "daily_lost_followers",
    "daily_new_followers",
    "daily_total_followers",
    "display_name",
    "email_clicks",
    "engaged_audience",
    "engagement_rate",
    "followers_count",
    "followers_growth_rate",
    "following_count",
    "is_business_account",
    "is_verified",
    "lead_submissions",
    "likes",
    "phone_number_clicks",
    "profile_deep_link",
    "profile_image",
    "profile_views",
    "shares",
    "total_likes",
    "unique_video_views",
    "username",
    "video_views",
    "videos_count",
]

BUSINESS_VIDEO_FIELDS = [
    "address_clicks",
    "app_download_clicks",
    "audience_cities",
    "audience_countries",
    "audience_genders",
    "audience_types",
    "average_time_watched",
    "caption",
    "comments",
    "create_time",
    "email_clicks",
    "embed_url",
    "engagement_likes",
    "favorites",
    "full_video_watched_rate",
    "impression_sources",
    "item_id",
    "lead_submissions",
    "likes",
    "media_type",
    "new_followers",
    "phone_number_clicks",
    "profile_views",
    "reach",
    "share_url",
    "shares",
    "thumbnail_url",
    "total_time_watched",
    "video_duration",
    "video_view_retention",
    "video_views",
    "website_clicks",
]


@dataclass
class TiktokOrganicAuthenticator(DeclarativeAuthenticator):
    """
    Custom authenticator that refreshes the TikTok access token using OAuth refresh_token flow.

    The CDK factory discovers fields via get_type_hints() and passes them as kwargs.
    The manifest evaluates {{ config['...'] }} Jinja templates and passes the resolved
    string values directly here — so no further interpolation is needed.
    """
    # These fields are discovered by the CDK via get_type_hints() and populated from
    # the manifest YAML (after Jinja template evaluation).
    config: Config
    client_key: Union[InterpolatedString, str]
    client_secret: Union[InterpolatedString, str]
    refresh_token: Union[InterpolatedString, str]
    parameters: InitVar[Mapping[str, Any]] = None

    def __post_init__(self, parameters: Mapping[str, Any] = None):
        self.logger = logging.getLogger("airbyte")
        self._access_token: Optional[str] = None
        self._parameters = parameters or {}
        self._client_key = InterpolatedString.create(self.client_key, parameters=self._parameters)
        self._client_secret = InterpolatedString.create(self.client_secret, parameters=self._parameters)
        self._refresh_token = InterpolatedString.create(self.refresh_token, parameters=self._parameters)

    def get_auth_header(self) -> Mapping[str, Any]:
        return {"Access-Token": self.get_token()}

    def get_token(self) -> str:
        if not self._access_token:
            self._access_token = self._refresh_access_token()
        return self._access_token

    @staticmethod
    def _load_config_from_file(path: str) -> Mapping[str, Any]:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, Mapping) else {}

    def _get_runtime_config(self) -> Mapping[str, Any]:
        runtime_config = self.config or self._parameters.get("config") or {}
        if isinstance(runtime_config, Mapping) and runtime_config:
            return runtime_config

        raw_runtime_config = os.getenv("SOURCE_TIKTOK_ORGANIC_CONFIG")
        if raw_runtime_config:
            try:
                parsed_runtime_config = json.loads(raw_runtime_config)
                if isinstance(parsed_runtime_config, str):
                    parsed_runtime_config = json.loads(parsed_runtime_config)
                if isinstance(parsed_runtime_config, Mapping) and parsed_runtime_config:
                    return parsed_runtime_config
            except json.JSONDecodeError as e:
                raise ValueError(f"Failed to parse SOURCE_TIKTOK_ORGANIC_CONFIG: {e}") from e

        config_path = os.getenv("SOURCE_TIKTOK_ORGANIC_CONFIG_PATH")
        fallback_paths = [p for p in [config_path, "./secrets/config.json", "/data/config.json"] if p]
        for path in fallback_paths:
            try:
                file_config = self._load_config_from_file(path)
                if file_config:
                    return file_config
            except (OSError, json.JSONDecodeError):
                continue

        return {}

    def _refresh_access_token(self) -> str:
        runtime_config = self._get_runtime_config()
        client_key = self._client_key.eval(runtime_config) or runtime_config.get("client_key", "")
        client_secret = self._client_secret.eval(runtime_config) or runtime_config.get("client_secret", "")
        refresh_token = self._refresh_token.eval(runtime_config) or runtime_config.get("refresh_token", "")

        if not client_key or not client_secret or not refresh_token:
            raise ValueError(
                "Missing TikTok auth values. Please provide non-empty client_key, client_secret, and refresh_token in the connector config."
            )

        response = requests.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Cache-Control": "no-cache",
            },
            data={
                "client_key": client_key,
                "client_secret": client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )

        if response.status_code != 200:
            response.raise_for_status()

        data = response.json()

        if data.get("error"):
            error_msg = data.get("error_description", data["error"])
            raise RuntimeError(f"TikTok API error: {error_msg}")

        return data["access_token"]


@dataclass
class TiktokOrganicRecordExtractor(RecordExtractor):
    """
    Custom record extractor for BusinessUser stream.
    TikTok returns account info with a list of daily 'metrics'.
    This extractor merges account info into each metric record.
    """
    _global_seen_dates_in_run: ClassVar[set[str]] = set()

    def __post_init__(self):
        self.logger = logging.getLogger("airbyte")

    def extract_records(self, response: requests.Response, **kwargs) -> Iterable[Mapping[str, Any]]:
        seen_dates = set()

        res_json = response.json()

        if res_json.get("code") != 0:
            code = res_json.get("code")
            message = res_json.get("message") or res_json.get("msg") or "Unknown TikTok API error"
            raise Exception(f"TikTok business endpoint error (code={code}): {message}")

        data = res_json.get("data", {})
        if not data:
            return []

        account_info = {k: v for k, v in data.items() if k != "metrics"}
        metrics = data.get("metrics", [])

        stream_slice = kwargs.get("stream_slice", {})
        slice_date = stream_slice.get("start_time") or stream_slice.get("start_date")
        slice_end_date = stream_slice.get("end_time") or stream_slice.get("end_date")

        if isinstance(slice_date, str) and len(slice_date) >= 10:
            slice_date = slice_date[:10]
        if isinstance(slice_end_date, str) and len(slice_end_date) >= 10:
            slice_end_date = slice_end_date[:10]

        for day_metrics in metrics:
            record = account_info.copy()
            record.update(day_metrics)

            metric_date = (
                day_metrics.get("date")
                or day_metrics.get("stat_time_day")
                or day_metrics.get("stat_time")
                or day_metrics.get("create_time")
                or slice_date
            )

            if isinstance(metric_date, str) and len(metric_date) >= 10:
                record["date"] = metric_date[:10]
            elif metric_date:
                record["date"] = str(metric_date)

            record_date = record.get("date")

            # Proper filtering (range only)
            if slice_date and record_date:
                if slice_end_date:
                    if not (slice_date <= record_date <= slice_end_date):
                        continue

            # Per-slice dedup
            if record_date:
                if record_date in seen_dates:
                    continue
                seen_dates.add(record_date)

            if record_date:
                if record_date in TiktokOrganicRecordExtractor._global_seen_dates_in_run:
                    continue
                TiktokOrganicRecordExtractor._global_seen_dates_in_run.add(record_date)

            yield record


@dataclass
class TiktokOrganicHttpRequester(HttpRequester):
    """
    Ensure TikTok `fields` query param is always sent as a JSON array string,
    equivalent to `json.dumps([...])` from manual tests.
    """

    @staticmethod
    def _normalize_date_for_tiktok(value: Any) -> Any:
        if not isinstance(value, str):
            return value
        match = re.match(r"^(\d{4}-\d{2}-\d{2})", value)
        if match:
            return match.group(1)
        return value

    @staticmethod
    def _load_runtime_config() -> Mapping[str, Any]:
        raw_runtime_config = os.getenv("SOURCE_TIKTOK_ORGANIC_CONFIG")
        if raw_runtime_config:
            try:
                parsed_runtime_config = json.loads(raw_runtime_config)
                if isinstance(parsed_runtime_config, str):
                    parsed_runtime_config = json.loads(parsed_runtime_config)
                if isinstance(parsed_runtime_config, Mapping):
                    return parsed_runtime_config
            except json.JSONDecodeError:
                pass

        config_path = os.getenv("SOURCE_TIKTOK_ORGANIC_CONFIG_PATH")
        fallback_paths = [p for p in [config_path, "./secrets/config.json", "/data/config.json"] if p]
        for path in fallback_paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, Mapping):
                        return data
            except (OSError, json.JSONDecodeError):
                continue
        return {}

    def get_request_params(
        self,
        *,
        stream_state: Optional[StreamState] = None,
        stream_slice: Optional[StreamSlice] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Mapping[str, Any]:

        params = dict(
            super().get_request_params(
                stream_state=stream_state,
                stream_slice=stream_slice,
                next_page_token=next_page_token,
            )
        )

        fields = params.get("fields")
        if isinstance(fields, list):
            params["fields"] = json.dumps(fields)

        # Make sure required TikTok identifiers are present even when declarative config
        # interpolation provides empty values in runtime context.
        runtime_config = self.config if isinstance(self.config, Mapping) and self.config else self._load_runtime_config()
        business_id = params.get("business_id") or runtime_config.get("business_id") or runtime_config.get("open_id")
        if business_id:
            params["business_id"] = business_id

        creator_id = params.get("creator_id") or runtime_config.get("creator_id")
        if creator_id:
            params["creator_id"] = creator_id

        # TikTok business endpoints expect YYYY-MM-DD for date filters.
        if "start_date" in params:
            params["start_date"] = self._normalize_date_for_tiktok(params.get("start_date"))
        if "end_date" in params:
            params["end_date"] = self._normalize_date_for_tiktok(params.get("end_date"))

        # -------------------------------
        # 1. Inject from slice
        # -------------------------------
        if stream_slice:
            start = stream_slice.get("start_time") or stream_slice.get("start_date")
            end = stream_slice.get("end_time") or stream_slice.get("end_date")

            if start:
                if isinstance(start, datetime.datetime):
                    params["start_date"] = start.strftime("%Y-%m-%d")
                else:
                    params["start_date"] = str(start)[:10]

            if end:
                if isinstance(end, datetime.datetime):
                    end_date = end.date()
                else:
                    end_date = datetime.datetime.strptime(str(end)[:10], "%Y-%m-%d").date()

                today = datetime.date.today()
                if end_date >= today:
                    end_date = today - datetime.timedelta(days=1)

                params["end_date"] = end_date.strftime("%Y-%m-%d")

        # -------------------------------
        # 2. First sync fallback
        # -------------------------------
        if not stream_state and "start_date" not in params:
            runtime_config = self.config
            if runtime_config.get("start_date"):
                params["start_date"] = runtime_config["start_date"]

        if "end_date" not in params:
            params["end_date"] = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        # -------------------------------
        # 3. Rolling window override
        # -------------------------------
        endpoint_hint = self.get_path(
            stream_state=stream_state,
            stream_slice=stream_slice,
            next_page_token=next_page_token,
        )

        if "business/get" in endpoint_hint:

            params["fields"] = json.dumps(BUSINESS_USER_FIELDS)

            if not hasattr(self, "_recent_mode"):
                state_date = None
                if isinstance(stream_state, Mapping):
                    state_date = stream_state.get("date")
                cli_has_state = os.getenv("SOURCE_TIKTOK_ORGANIC_HAS_STATE", "0") == "1"
                self._recent_mode = bool(state_date) or cli_has_state

            if self._recent_mode:
                today = datetime.date.today()
                end = today - datetime.timedelta(days=1)
                start = today - datetime.timedelta(days=7)

                params["start_date"] = start.strftime("%Y-%m-%d")
                params["end_date"] = end.strftime("%Y-%m-%d")

        elif "business/video/list" in endpoint_hint:
            params["fields"] = json.dumps(BUSINESS_VIDEO_FIELDS)

        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("[STREAM STATE] %s", stream_state)
            self.logger.debug("[STREAM SLICE] %s", stream_slice)
            self.logger.debug("[REQUEST PARAMS] %s", params)

        return params
