from __future__ import annotations

import logging
from datetime import date, timedelta, datetime
from typing import Mapping, Any, List, Tuple, Callable

from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream

from source_odnoklassniki_groups.auth import CredentialsCraftAuthenticator, OKCredentials
from source_odnoklassniki_groups.streams import GetStatTrendsStream, check_group_stream_connection
from source_odnoklassniki_groups.types import IsSuccess, Message, StartDate, EndDate


class SourceOdnoklassnikiGroups(AbstractSource):
    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        credentials = self._get_auth(config)()
        date_from, date_to = self._prepare_dates(config)
        gids = config.get("gids")
        return [
            GetStatTrendsStream(credentials=credentials, gids=gids, date_from=date_from, date_to=date_to),
        ]

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[IsSuccess, Message | None]:
        # Check connection to CredentialsCraft
        auth = self._get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            is_success, message = auth.check_connection()
            if not is_success:
                return False, f"Failed to connect to CredentialsCraft: {message}"

        credentials = auth()

        # Check ads config
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
                token_id=credentials["credentials_craft_token_id"],
            )
        if auth_type == "token_auth":
            return lambda: OKCredentials(
                application_id=credentials["application_id"],
                application_key=credentials["application_key"],
                application_secret_key=credentials["application_secret_key"],
                access_token=credentials["access_token"],
                session_secret_key=credentials["session_secret_key"],
            )

        raise ValueError(f"Unknown auth type: '{auth_type}'")

    @staticmethod
    def _prepare_dates(config: Mapping[str, Any]) -> Tuple[StartDate | None, EndDate | None]:
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

        return date_from, date_to

    @staticmethod
    def _check_config(config: Mapping[str, Any], credentials: OKCredentials) -> Tuple[IsSuccess, Message | None]:
        # Check gids
        if not config.get("gids"):
            return False, "Group IDs not set"

        # Check dates config
        date_from = config.get("date_from")
        date_to = config.get("date_to")
        if date_from and date_to:
            if datetime.fromisoformat(date_from) > datetime.fromisoformat(date_to):
                return False, "'Date from' exceeds 'Date to' in config"

        # Check connection
        is_success, message = check_group_stream_connection(credentials=credentials, gid=config.get("gids")[0])
        if not is_success:
            return is_success, message

        return True, None
