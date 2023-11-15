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

from .reports.reports import (
    AdGroupReport,
    AdGroupTargetingReport,
    AdvertizerReport,
    AdvertizerTargetingReport,
    CampaignTargetingReport,
    KeywordReport,
    PinPromotionReport,
    PinPromotionTargetingReport,
    ProductGroupReport,
    ProductGroupTargetingReport,
    ProductItemReport,
)
from .streams import (
    AdAccountAnalytics,
    AdAccounts,
    AdAnalytics,
    AdGroupAnalytics,
    AdGroups,
    Ads,
    Audiences,
    BoardPins,
    Boards,
    BoardSectionPins,
    BoardSections,
    CampaignAnalytics,
    Campaigns,
    Catalogs,
    CatalogsFeeds,
    CatalogsProductGroups,
    ConversionTags,
    CustomerLists,
    Keywords,
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
        try:
            auth_headers = {"Accept": "application/json", **authenticator.get_auth_header()}
            session = requests.get(url, headers=auth_headers)
            session.raise_for_status()
            return True, None
        except requests.exceptions.HTTPError as e:
            if "401 Client Error: Unauthorized for url" in str(e):
                return False, f"Try to re-authenticate because current refresh token is not valid. {e}"
            else:
                return False, e
        except requests.exceptions.RequestException as e:
            return False, e

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = self.get_authenticator(config)
        report_config = self._validate_and_transform(config, amount_of_days_allowed_for_lookup=913)
        config = self._validate_and_transform(config)
        status = ",".join(config.get("status")) if config.get("status") else None

        ad_accounts = AdAccounts(config)
        ads = Ads(ad_accounts, config=config, status_filter=status)
        ad_groups = AdGroups(ad_accounts, config=config, status_filter=status)
        campaigns = Campaigns(ad_accounts, config=config, status_filter=status)
        boards = Boards(config)
        board_sections = BoardSections(boards, config=config)
        return [
            ad_accounts,
            AdAccountAnalytics(ad_accounts, config=config),
            ads,
            AdAnalytics(ads, config=config),
            ad_groups,
            AdGroupAnalytics(ad_groups, config=config),
            boards,
            BoardPins(boards, config=config),
            board_sections,
            BoardSectionPins(board_sections, config=config),
            campaigns,
            CampaignAnalytics(campaigns, config=config),
            CampaignAnalyticsReport(ad_accounts, config=report_config),
            CampaignTargetingReport(ad_accounts, config=report_config),
            UserAccountAnalytics(None, config=config),
            Keywords(ad_groups, config=config),
            Audiences(ad_accounts, config=config),
            ConversionTags(ad_accounts, config=config),
            CustomerLists(ad_accounts, config=config),
            Catalogs(config=config),
            CatalogsFeeds(config=config),
            CatalogsProductGroups(config=config),
            AdvertizerReport(ad_accounts, config=report_config),
            AdvertizerTargetingReport(ad_accounts, config=report_config),
            AdGroupReport(ad_accounts, config=report_config),
            AdGroupTargetingReport(ad_accounts, config=report_config),
            PinPromotionReport(ad_accounts, config=report_config),
            PinPromotionTargetingReport(ad_accounts, config=report_config),
            ProductGroupReport(ad_accounts, config=report_config),
            ProductGroupTargetingReport(ad_accounts, config=report_config),
            KeywordReport(ad_accounts, config=report_config),
            ProductItemReport(ad_accounts, config=report_config),
        ]
