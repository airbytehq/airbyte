from __future__ import annotations

import logging
from datetime import date, timedelta, datetime
from typing import Mapping, Any, List, Tuple

import pytz
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_wildberries_seller.auth import CredentialsCraftAuthenticator
from source_wildberries_seller.streams import (
    DetailNmReportStream,
    GroupedNmReportStream,
    DetailHistoryNmReportStream,
    GroupedHistoryNmReportStream,
    check_content_analytics_stream_connection,
)
from source_wildberries_seller.types import StartDate, EndDate, IsSuccess, Message, WildberriesCredentials


class SourceWildberriesSeller(AbstractSource):
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        credentials = self._get_auth(config)()
        content_analytics_date_from, content_analytics_date_to = self._prepare_dates(config)
        content_analytics_brand_names = config.get("brand_names", [])
        content_analytics_object_ids = config.get("object_ids", [])
        content_analytics_tag_ids = config.get("tag_ids", [])
        content_analytics_nm_ids = config.get("nm_ids", [])
        content_analytics_timezone = config.get("timezone")
        content_analytics_aggregation_level = config.get("aggregation_level")

        return [
            DetailNmReportStream(
                credentials=credentials,
                date_from=content_analytics_date_from,
                date_to=content_analytics_date_to,
                brand_names=content_analytics_brand_names,
                object_ids=content_analytics_object_ids,
                tag_ids=content_analytics_tag_ids,
                nm_ids=content_analytics_nm_ids,
                timezone=content_analytics_timezone,
            ),
            GroupedNmReportStream(
                credentials=credentials,
                date_from=content_analytics_date_from,
                date_to=content_analytics_date_to,
                object_ids=content_analytics_object_ids,
                brand_names=content_analytics_brand_names,
                tag_ids=content_analytics_tag_ids,
                timezone=content_analytics_timezone,
            ),
            DetailHistoryNmReportStream(
                credentials=credentials,
                date_from=content_analytics_date_from,
                date_to=content_analytics_date_to,
                nm_ids=content_analytics_nm_ids,
                timezone=content_analytics_timezone,
                aggregation_level=content_analytics_aggregation_level,
            ),
            GroupedHistoryNmReportStream(
                credentials=credentials,
                date_from=content_analytics_date_from,
                date_to=content_analytics_date_to,
                object_ids=content_analytics_object_ids,
                brand_names=content_analytics_brand_names,
                tag_ids=content_analytics_tag_ids,
                timezone=content_analytics_timezone,
                aggregation_level=content_analytics_aggregation_level,
            ),
        ]

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[IsSuccess, Message | None]:
        # Check connection to CredentialsCraft
        auth = self._get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            is_success, message = auth.check_connection()
            if not is_success:
                return False, f"Failed to connect to CredentialsCraft: {message}"

        credentials = auth()

        # Check content analytics config
        is_success, message = self._check_content_analytics_config(config=config, credentials=credentials)
        if not is_success:
            return is_success, message

        return True, None

    @staticmethod
    def _get_auth(config: Mapping[str, Any]) -> CredentialsCraftAuthenticator:
        credentials = config["credentials"]
        auth_type = credentials["auth_type"]
        if auth_type == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                host=credentials["credentials_craft_host"],
                bearer_token=credentials["credentials_craft_token"],
                token_id=credentials["credentials_craft_wildberries_token_id"],
            )
        raise ValueError(f"Unknown auth type: '{auth_type}'")

    @staticmethod
    def _prepare_dates(config: Mapping[str, Any]) -> Tuple[StartDate, EndDate]:
        if date_from := config.get("date_from"):
            date_to = config.get("date_to", (date.today() - timedelta(days=1)).isoformat())
            return date.fromisoformat(date_from), date.fromisoformat(date_to)

        last_days = config.get("last_days")
        date_from = date.today() - timedelta(days=last_days)
        date_to = date.today() - timedelta(days=1)  # yesterday
        return date_from, date_to

    @staticmethod
    def _check_content_analytics_config(config: Mapping[str, Any], credentials: WildberriesCredentials) -> Tuple[IsSuccess, Message | None]:
        # Check dates config
        date_from = config.get("date_from")
        date_to = config.get("date_to")
        last_days = config.get("last_days")

        if not (last_days or (date_from and date_to)):
            message = "You must specify either 'Date from' and 'Date to' or just 'Load last N days' params in content_analytics config"
            return False, message

        if date_from and date_to:
            if datetime.fromisoformat(date_from) > datetime.fromisoformat(date_to):
                return False, "'Date from' exceeds 'Date to' in content_analytics config"

        if timezone := config.get("timezone"):
            try:
                pytz.timezone(timezone)
            except pytz.UnknownTimeZoneError:
                return False, f"Invalid timezone in content_analytics config: '{timezone}'"

        # Check connection
        is_success, message = check_content_analytics_stream_connection(credentials=credentials)
        if not is_success:
            return is_success, message

        return True, None
