#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping

from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource
from airbyte_cdk.sources.streams import Stream

logger = logging.getLogger("airbyte")
DOCUMENTATION_URL = "https://docs.airbyte.com/integrations/sources/tiktok-marketing"
SANDBOX_STREAM_NAMES = [
    "ad_group_audience_reports_by_country_daily",
    "ad_group_audience_reports_by_platform_daily",
    "ad_group_audience_reports_daily",
    "ad_groups",
    "ad_groups_reports_daily",
    "ad_groups_reports_hourly",
    "ad_groups_reports_lifetime",
    "ads",
    "ads_audience_reports_by_country_daily",
    "ads_audience_reports_by_platform_daily",
    "ads_audience_reports_by_province_daily",
    "ads_audience_reports_daily",
    "ads_reports_daily",
    "ads_reports_hourly",
    "ads_reports_lifetime",
    "advertisers",
    "audiences",
    "campaigns",
    "campaigns_audience_reports_by_country_daily",
    "campaigns_audience_reports_by_platform_daily",
    "campaigns_audience_reports_daily",
    "campaigns_reports_daily",
    "campaigns_reports_hourly",
    "campaigns_reports_lifetime",
    "creative_assets_images",
    "creative_assets_music",
    "creative_assets_portfolios",
    "creative_assets_videos",
]


class SourceTiktokMarketing(YamlDeclarativeSource):
    def __init__(self):
        super().__init__(**{"path_to_yaml": "manifest.yaml"})

    @staticmethod
    def _is_sandbox(config: Mapping[str, Any]) -> bool:
        credentials = config.get("credentials")
        if credentials:
            is_sandbox = credentials["auth_type"] == "sandbox_access_token"
        else:
            secret = config.get("environment", {}).get("secret")
            is_sandbox = secret is None

        return is_sandbox

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        is_production = not self._is_sandbox(config)
        streams = super().streams(config)

        if is_production:
            return streams

        sandbox_streams = [stream for stream in streams if stream.name in SANDBOX_STREAM_NAMES]
        return sandbox_streams
