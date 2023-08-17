#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
from base64 import standard_b64encode
from typing import Any, List, Mapping, Tuple

import pendulum
import requests
from airbyte_cdk.models import FailureType
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.auth import Oauth2Authenticator
from airbyte_cdk.utils import AirbyteTracedException
from source_pinterest.reports import CampaignAnalyticsReport

from .streams import (
    AdAccountAnalytics,
    AdAccounts,
    AdAnalytics,
    AdGroupAnalytics,
    AdGroups,
    Ads,
    BoardPins,
    Boards,
    BoardSectionPins,
    BoardSections,
    CampaignAnalytics,
    Campaigns,
    PinterestStream,
    UserAccountAnalytics,
)


class SourcePinterest(AbstractSource):
    def _validate_and_transform(self, config: Mapping[str, Any], amount_of_days_allowed_for_lookup: int = 89):
        config = copy.deepcopy(config)
        today = pendulum.today()
        latest_date_allowed_by_api = today.subtract(days=amount_of_days_allowed_for_lookup)

        start_date = config["start_date"]
        if not start_date:
            config["start_date"] = latest_date_allowed_by_api
        else:
            try:
                config["start_date"] = pendulum.from_format(config["start_date"], "YYYY-MM-DD")
            except ValueError:
                message = "Entered `Start Date` does not match format YYYY-MM-DD"
                raise AirbyteTracedException(
                    message=message,
                    internal_message=message,
                    failure_type=FailureType.config_error,
                )
            if (today - config["start_date"]).days > amount_of_days_allowed_for_lookup:
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
        config["authenticator"] = self.get_authenticator(config)
        report_config = self._validate_and_transform(config, amount_of_days_allowed_for_lookup=913)
        config = self._validate_and_transform(config)
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
            CampaignAnalyticsReport(AdAccounts(report_config), config=report_config),
            Campaigns(AdAccounts(config), status_filter=status, config=config),
            UserAccountAnalytics(None, config=config),
        ]
