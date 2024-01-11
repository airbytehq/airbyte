from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Mapping, Any, List, Tuple, Callable

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_ozon.auth import CredentialsCraftAuthenticator, fetch_ozon_token, OzonToken
from source_ozon.streams import CampaignsReportStream, check_ozon_api_connection
from source_ozon.types import IsSuccess, Message, StartDate, EndDate


class SourceOzon(AbstractSource):
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        credentials = self._get_auth(config)()
        date_from, date_to = self._prepare_dates(config)
        return [
            CampaignsReportStream(credentials=credentials, date_from=date_from, date_to=date_to),
        ]

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[IsSuccess, Message | None]:
        # Check auth
        auth = self._get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            is_success, message = auth.check_connection()
            if not is_success:
                return False, f"Failed to connect to CredentialsCraft: {message}"

        credentials = auth()

        # Check config
        is_success, message = self._check_config(config=config, credentials=credentials)
        if not is_success:
            return is_success, message

        return True, None

    @staticmethod
    def _get_auth(config: Mapping[str, Any]) -> Callable:
        credentials = config["credentials"]
        auth_type = credentials["auth_type"]

        if auth_type == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                host=credentials["credentials_craft_host"],
                bearer_token=credentials["credentials_craft_token"],
                token_id=credentials["credentials_craft_ozon_token_id"],
            )

        if auth_type == "token_auth":
            return lambda: fetch_ozon_token(client_id=credentials["client_id"], client_secret=credentials["client_secret"])

        raise ValueError(f"Unknown auth type: '{auth_type}'")

    @staticmethod
    def _check_config(config: Mapping[str, Any], credentials: OzonToken) -> Tuple[IsSuccess, Message | None]:
        # Check dates config
        if last_days := config.get("last_days"):
            if last_days > 62:
                return False, "Last days exceeds 62 days"

        date_from = config.get("date_from")
        date_to = config.get("date_to")
        if date_from and date_to:
            date_from_dt = date.fromisoformat(date_from)
            date_to_dt = date.fromisoformat(date_to)
            if date_from_dt > date_to_dt:
                return False, "'Date from' exceeds 'Date to' in config"
            if (date_to_dt - date_from_dt).days > 62:
                return False, "Date range exceeds 62 days"

        # Check connection
        is_success, message = check_ozon_api_connection(credentials=credentials)
        if not is_success:
            return is_success, message

        return True, None

    @staticmethod
    def _prepare_dates(config: Mapping[str, Any]) -> Tuple[StartDate | None, EndDate | None]:
        if last_days := config.get("last_days"):
            date_from = date.today() - timedelta(days=last_days)
            date_to = date.today() - timedelta(days=1)  # yesterday
            return date_from, date_to

        default_date_from = default_date_to = date.today() - timedelta(days=1)  # yesterday
        date_from_str = config.get("date_from")
        date_to_str = config.get("date_to")
        date_from = date.fromisoformat(date_from_str) if date_from_str else default_date_from
        date_to = date.fromisoformat(date_to_str) if date_to_str else default_date_to
        return date_from, date_to
