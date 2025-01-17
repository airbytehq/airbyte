#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from logging import Logger
from typing import Any, List, Mapping, Optional, Tuple

import pendulum
from airbyte_protocol_dataclasses.models import ConfiguredAirbyteCatalog
from requests import HTTPError

from airbyte_cdk import TState
from airbyte_cdk.models import ConnectorSpecification, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException, is_cloud_environment
from source_amazon_seller_partner.auth import AWSAuthenticator
from source_amazon_seller_partner.constants import get_marketplaces
from source_amazon_seller_partner.streams import (
    BrandAnalyticsMarketBasketReports,
    BrandAnalyticsRepeatPurchaseReports,
    BrandAnalyticsSearchTermsReports,
    NetPureProductMarginReport,
    RapidRetailAnalyticsInventoryReport,
    ReportsAmazonSPStream,
    SellerAnalyticsSalesAndTrafficReports,
    VendorForecastingFreshReport,
    VendorForecastingRetailReport,
    VendorInventoryReports,
    VendorSalesReports,
    VendorTrafficReport,
)
from source_amazon_seller_partner.utils import AmazonConfigException


# given the retention period: 730
DEFAULT_RETENTION_PERIOD_IN_DAYS = 730

from source_amazon_seller_partner.components.auth import AmazonSPOauthAuthenticator


class SourceAmazonSellerPartner(YamlDeclarativeSource):
    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    @staticmethod
    def get_aws_config_settings(config: Mapping[str, Any]) -> Mapping[str, Any]:
        endpoint, marketplace_id, _ = get_marketplaces(config.get("aws_environment"))[config.get("region")]
        return {"endpoint": endpoint, "marketplace_id": marketplace_id}

    @staticmethod
    def _get_stream_kwargs(config: Mapping[str, Any]) -> Mapping[str, Any]:
        endpoint, marketplace_id, _ = get_marketplaces(config.get("aws_environment"))[config.get("region")]
        auth = AmazonSPOauthAuthenticator(
            config=config,
            parameters={},
            token_refresh_endpoint="https://api.amazon.com/auth/o2/token",
            client_id=config.get("lwa_app_id"),
            client_secret=config.get("lwa_client_secret"),
            refresh_token=config.get("refresh_token"),
            host=endpoint.replace("https://", ""),
        )

        start_date = config.get("replication_start_date")
        use_default_start_date = (
            not start_date or (pendulum.now("utc") - pendulum.parse(start_date)).days > DEFAULT_RETENTION_PERIOD_IN_DAYS
        )
        if use_default_start_date:
            start_date = pendulum.now("utc").subtract(days=DEFAULT_RETENTION_PERIOD_IN_DAYS).strftime("%Y-%m-%dT%H:%M:%SZ")

        end_date = config.get("replication_end_date")
        use_default_end_date = not end_date or end_date < start_date
        if use_default_end_date:
            end_date = None  # None to sync all data

        stream_kwargs = {
            "url_base": endpoint,
            "authenticator": auth,
            "replication_start_date": start_date,
            "marketplace_id": marketplace_id,
            "period_in_days": config.get("period_in_days", 365),
            "replication_end_date": end_date,
        }
        return stream_kwargs

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        """
        :param config: A Mapping of the user input configuration as defined in the connector spec.
        """
        config.update(self.get_aws_config_settings(config))
        streams = super().streams(config)
        # return low_code_streams
        self.validate_stream_report_options(config)
        # streams = []
        stream_kwargs = self._get_stream_kwargs(config)
        stream_list = [
            VendorForecastingFreshReport,  # remove in favor of using low-code analytics streams
            VendorForecastingRetailReport,
        ]

        # TODO: Remove after Brand Analytics will be enabled in CLOUD: https://github.com/airbytehq/airbyte/issues/32353
        if not is_cloud_environment():
            brand_analytics_reports = [
                # Uncomment this to reuse the legacy Python
                # BrandAnalyticsMarketBasketReports,
                BrandAnalyticsSearchTermsReports,
                BrandAnalyticsRepeatPurchaseReports,
                SellerAnalyticsSalesAndTrafficReports,
                VendorSalesReports,
                VendorInventoryReports,
                NetPureProductMarginReport,
                RapidRetailAnalyticsInventoryReport,
                VendorTrafficReport,
            ]
            stream_list += brand_analytics_reports

        for stream in stream_list:
            if not issubclass(stream, ReportsAmazonSPStream):
                streams.append(stream(**stream_kwargs))
                continue
            report_kwargs = list(self.get_stream_report_kwargs(stream.report_name, config))
            if not report_kwargs:
                report_kwargs.append((stream.report_name, {}))
            for name, options in report_kwargs:
                kwargs = {
                    "stream_name": name,
                    "report_options": options,
                    "wait_to_avoid_fatal_errors": config.get("wait_to_avoid_fatal_errors", False),
                    **stream_kwargs,
                }
                streams.append(stream(**kwargs))
        return streams

    def spec(self, logger: Logger) -> ConnectorSpecification:
        spec = super().spec(logger)
        if not is_cloud_environment():
            oss_only_streams = [
                "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT",
                "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT",
                "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT",
                "GET_SALES_AND_TRAFFIC_REPORT",
                "GET_VENDOR_SALES_REPORT",
                "GET_VENDOR_INVENTORY_REPORT",
                "GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT",
                "GET_VENDOR_TRAFFIC_REPORT",
            ]
            spec.connectionSpecification["properties"]["report_options_list"]["items"]["properties"]["report_name"]["enum"].extend(
                oss_only_streams
            )

        return spec

    @staticmethod
    def validate_replication_dates(config: Mapping[str, Any]) -> None:
        if (
            "replication_start_date" in config
            and "replication_end_date" in config
            and config["replication_end_date"] < config["replication_start_date"]
        ):
            raise AmazonConfigException(message="End Date should be greater than or equal to Start Date")

    @staticmethod
    def validate_stream_report_options(config: Mapping[str, Any]) -> None:
        options_list = config.get("report_options_list", [])
        stream_names = [x.get("stream_name") for x in options_list]
        if len(stream_names) != len(set(stream_names)):
            raise AmazonConfigException(message="Stream name should be unique among all Report options list")

        for report_option in options_list:
            option_names = [x.get("option_name") for x in report_option.get("options_list")]
            if len(option_names) != len(set(option_names)):
                raise AmazonConfigException(
                    message=f"Option names should be unique for `{report_option.get('stream_name')}` report options"
                )

    @staticmethod
    def get_stream_report_kwargs(report_name: str, config: Mapping[str, Any]) -> List[Tuple[str, Optional[List[Mapping[str, Any]]]]]:
        options_list = config.get("report_options_list", [])
        for x in options_list:
            if x.get("report_name") == report_name:
                yield x.get("stream_name"), x.get("options_list")
