from __future__ import annotations

import logging
from datetime import date, timedelta, datetime
from typing import Mapping, Any, List, Tuple

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_wildberries_statistics.auth import CredentialsCraftAuthenticator
from source_wildberries_statistics.streams import (
    IncomeStream,
    StockStream,
    OrderStream,
    ReportDetailByPeriodStream,
    SaleStream,
    check_statistics_stream_connection,
)
from source_wildberries_statistics.types import StartDate, EndDate, WildberriesCredentials, IsSuccess, Message


class SourceWildberriesStatistics(AbstractSource):
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        credentials = self._get_auth(config)()
        statistics_date_from, statistics_date_to = self._prepare_dates(config)
        statistics_strict_date_from = config.get("strict_date_from", False)

        return [
            IncomeStream(credentials=credentials, date_from=statistics_date_from),
            StockStream(credentials=credentials, date_from=statistics_date_from),
            OrderStream(credentials=credentials, date_from=statistics_date_from, strict_date_from=statistics_strict_date_from),
            SaleStream(credentials=credentials, date_from=statistics_date_from, strict_date_from=statistics_strict_date_from),
            ReportDetailByPeriodStream(credentials=credentials, date_from=statistics_date_from, date_to=statistics_date_to),
        ]

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[IsSuccess, Message | None]:
        # Check connection to CredentialsCraft
        auth = self._get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            is_success, message = auth.check_connection()
            if not is_success:
                return False, f"Failed to connect to CredentialsCraft: {message}"

        credentials = auth()

        # Check statistics config
        is_success, message = self._check_statistics_config(config=config, credentials=credentials)
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
    def _check_statistics_config(config: Mapping[str, Any], credentials: WildberriesCredentials) -> Tuple[IsSuccess, Message | None]:
        # Check dates config
        date_from = config.get("date_from")
        last_days = config.get("last_days")
        if not (date_from or last_days):
            message = "You must specify either 'Date from' or just 'Load last N days' params in statistics config"
            return False, message

        date_to = config.get("date_to")
        if date_from and date_to:
            if datetime.fromisoformat(date_from) > datetime.fromisoformat(date_to):
                return False, "'Date from' exceeds 'Date to' in statistics config"

        # Check connection
        is_success, message = check_statistics_stream_connection(credentials=credentials)
        if not is_success:
            return is_success, message

        return True, None
