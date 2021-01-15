"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
from typing import Dict
from googleads import adwords, oauth2
from tap_adwords import VERSION

from airbyte_protocol import AirbyteCatalog, AirbyteConnectionStatus, Status
from base_python import AirbyteLogger, CatalogHelper
from base_singer import SingerSource, SyncModeInfo, SyncMode


class SourceGoogleAdwordsSinger(SingerSource):
    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        # get customers info to verify credentials and permissions
        # https://developers.google.com/adwords/api/docs/reference/v201809/CustomerService#getcustomers
        try:
            customer_ids = config['customer_ids'].split(",")
            for customer_id in customer_ids:
                oauth2_client = oauth2.GoogleRefreshTokenClient(config['oauth_client_id'],
                                                                config['oauth_client_secret'],
                                                                config['refresh_token'])

                sdk_client = adwords.AdWordsClient(config['developer_token'],
                                                   oauth2_client, user_agent=config['user_agent'],
                                                   client_customer_id=customer_id)
                customer_info = sdk_client.GetService(service_name='CustomerService', version=VERSION).getCustomers()
                if not customer_info:
                    return AirbyteConnectionStatus(status=Status.FAILED)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{str(e)}")

    def get_sync_mode_overrides(self) -> Dict[str, SyncModeInfo]:
        incremental_streams = [
            "ACCOUNT_PERFORMANCE_REPORT", "AD_PERFORMANCE_REPORT", "ADGROUP_PERFORMANCE_REPORT",
            "AGE_RANGE_PERFORMANCE_REPORT", "AUDIENCE_PERFORMANCE_REPORT", "CALL_METRICS_CALL_DETAILS_REPORT",
            "CAMPAIGN_PERFORMANCE_REPORT", "CLICK_PERFORMANCE_REPORT", "CRITERIA_PERFORMANCE_REPORT",
            "DISPLAY_KEYWORD_PERFORMANCE_REPORT", "DISPLAY_TOPICS_PERFORMANCE_REPORT", "FINAL_URL_REPORT",
            "GENDER_PERFORMANCE_REPORT", "GEO_PERFORMANCE_REPORT", "KEYWORDLESS_QUERY_REPORT",
            "KEYWORDS_PERFORMANCE_REPORT", "SEARCH_QUERY_PERFORMANCE_REPORT", "VIDEO_PERFORMANCE_REPORT"
        ]

        full_refresh_streams = ["accounts", "ad_groups", "campaigns", "ads",
                                "PLACEHOLDER_FEED_ITEM_REPORT", "PLACEMENT_PERFORMANCE_REPORT",
                                "SHOPPING_PERFORMANCE_REPORT", "PLACEHOLDER_REPORT", ]
        overrides = {}
        for stream_name in incremental_streams:
            overrides[stream_name] = SyncModeInfo(supported_sync_modes=[SyncMode.incremental])
        for stream_name in full_refresh_streams:
            overrides[stream_name] = SyncModeInfo(supported_sync_modes=[SyncMode.full_refresh])
        return overrides

    def discover_cmd(self, logger, config_path) -> str:
        return f"tap-adwords --config {config_path} --discover"

    def read_cmd(self, logger, config_path, catalog_path, state_path=None) -> str:
        config_option = f"--config {config_path}"
        properties_option = f"--properties {catalog_path}"
        return f"tap-adwords {config_option} {properties_option}"

    def transform_config(self, raw_config):
        # required property in the singer tap, but seems like an implementation detail of stitch
        # https://github.com/singer-io/tap-adwords/blob/cf0c1ff7dae8503f97173a15cf8d78bf975069f8/tap_adwords/__init__.py#L963-L969
        raw_config["user_agent"] = "unknown"
        return raw_config
