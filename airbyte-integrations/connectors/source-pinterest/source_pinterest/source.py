#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import copy
import logging
from base64 import standard_b64encode
from typing import Any, List, Mapping

import pendulum

from airbyte_cdk.models import FailureType
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.requests_native_auth import Oauth2Authenticator
from airbyte_cdk.utils import AirbyteTracedException
from source_pinterest.reports import CampaignAnalyticsReport

from .python_stream_auth import PinterestOauthAuthenticator
from .reports.reports import (
    AdGroupReport,
    AdGroupTargetingReport,
    AdvertiserReport,
    AdvertiserTargetingReport,
    CampaignTargetingReport,
    CustomReport,
    KeywordReport,
    PinPromotionReport,
    PinPromotionTargetingReport,
    ProductGroupReport,
    ProductGroupTargetingReport,
    ProductItemReport,
)
from .streams import PinterestStream


logger = logging.getLogger("airbyte")


class SourcePinterest(YamlDeclarativeSource):
    def __init__(self) -> None:
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    @staticmethod
    def _validate_and_transform(config: Mapping[str, Any], amount_of_days_allowed_for_lookup: int = 89) -> Mapping[str, Any]:
        config = copy.deepcopy(config)
        today = pendulum.today()
        latest_date_allowed_by_api = today.subtract(days=amount_of_days_allowed_for_lookup)

        start_date = config.get("start_date")

        # transform to datetime
        if start_date and isinstance(start_date, str):
            try:
                config["start_date"] = pendulum.from_format(start_date, "YYYY-MM-DD")
            except ValueError:
                message = f"Entered `Start Date` {start_date} does not match format YYYY-MM-DD"
                raise AirbyteTracedException(
                    message=message,
                    internal_message=message,
                    failure_type=FailureType.config_error,
                )

        if not start_date or config["start_date"] < latest_date_allowed_by_api:
            logger.info(
                f"Current start_date: {start_date} does not meet API report requirements. "
                f"Resetting start_date to: {latest_date_allowed_by_api}"
            )
            config["start_date"] = latest_date_allowed_by_api

        return config

    @staticmethod
    def get_authenticator(config) -> Oauth2Authenticator:
        config = config.get("credentials") or config
        credentials_base64_encoded = standard_b64encode(
            (config.get("client_id") + ":" + config.get("client_secret")).encode("ascii")
        ).decode("ascii")
        auth = f"Basic {credentials_base64_encoded}"

        return PinterestOauthAuthenticator(
            token_refresh_endpoint=f"{PinterestStream.url_base}oauth/token",
            client_secret=config.get("client_secret"),
            client_id=config.get("client_id"),
            refresh_access_token_headers={"Authorization": auth},
            refresh_token=config.get("refresh_token"),
        )

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        config["authenticator"] = self.get_authenticator(config)
        report_config = self._validate_and_transform(config, amount_of_days_allowed_for_lookup=913)

        declarative_streams = super().streams(config)

        # Report streams involve async data fetch, which is currently not supported in low-code
        report_streams = [
            CampaignAnalyticsReport(self._create_ad_accounts_stream(config), config=report_config),
            CampaignTargetingReport(self._create_ad_accounts_stream(config), config=report_config),
            AdvertiserReport(self._create_ad_accounts_stream(config), config=report_config),
            AdvertiserTargetingReport(self._create_ad_accounts_stream(config), config=report_config),
            AdGroupReport(self._create_ad_accounts_stream(config), config=report_config),
            AdGroupTargetingReport(self._create_ad_accounts_stream(config), config=report_config),
            PinPromotionReport(self._create_ad_accounts_stream(config), config=report_config),
            PinPromotionTargetingReport(self._create_ad_accounts_stream(config), config=report_config),
            ProductGroupReport(self._create_ad_accounts_stream(config), config=report_config),
            ProductGroupTargetingReport(self._create_ad_accounts_stream(config), config=report_config),
            KeywordReport(self._create_ad_accounts_stream(config), config=report_config),
            ProductItemReport(self._create_ad_accounts_stream(config), config=report_config),
        ] + self.get_custom_report_streams(config=report_config)

        return declarative_streams + report_streams

    def _create_ad_accounts_stream(self, config):
        """
        Sync the recent changes in RFR, it is not possible to re-use the same stream as a parent stream as after a full refresh of the
        parent stream, the internal state of the parent stream will switch to FULL_REFRESH_SYNC_COMPLETE_KEY and will prevent syncing any
        more records. Hence, each parents need to have their own parent stream.

        In terms of caching, this parent stream wasn't cache on version 2.0.3 so we would do two calls to
        "https://api.pinterest.com/v5/ad_accounts" for each stream: one during the availability strategy and one during the read. This means
        that this change should not impact performance.
        """
        return [stream for stream in super().streams(config) if stream.name == "ad_accounts"][0]

    def get_custom_report_streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """return custom report streams"""
        custom_streams = []
        for report_config in config.get("custom_reports", []):
            report_config["authenticator"] = config["authenticator"]

            # https://developers.pinterest.com/docs/api/v5/#operation/analytics/get_report
            if report_config.get("granularity") == "HOUR":
                # Otherwise: Response Code: 400 {"code":1,"message":"HOURLY request must be less than 3 days"}
                amount_of_days_allowed_for_lookup = 2
            elif report_config.get("level") == "PRODUCT_ITEM":
                amount_of_days_allowed_for_lookup = 91
            else:
                amount_of_days_allowed_for_lookup = 913

            start_date = report_config.get("start_date")
            if not start_date:
                report_config["start_date"] = config.get("start_date")

            report_config = self._validate_and_transform(report_config, amount_of_days_allowed_for_lookup)

            stream = CustomReport(parent=self._create_ad_accounts_stream(config), config=report_config)
            custom_streams.append(stream)
        return custom_streams
