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
import sys
from typing import Dict, List

from airbyte_protocol import AirbyteConnectionStatus, Status
from base_python import AirbyteLogger
from base_singer import SingerSource, SyncMode, SyncModeInfo
from googleads import adwords, oauth2
from tap_adwords import VERSION


class SourceGoogleAdwordsSinger(SingerSource):
    @staticmethod
    def _get_accounts(logger: AirbyteLogger, sdk_client: adwords.AdWordsClient, selector: Dict):
        # obtaining accounts for customer_id
        managed_customer_page = sdk_client.GetService(service_name="ManagedCustomerService", version=VERSION).get(selector)
        accounts = managed_customer_page.entries
        return accounts

    def _check_internal(self, logger: AirbyteLogger, streams: List, config: json):
        # checking if REPORT syncing will be called for manager account
        # https://developers.google.com/adwords/api/docs/common-errors#ReportDefinitionError.CUSTOMER_SERVING_TYPE_REPORT_MISMATCH
        try:
            customer_ids = config["customer_ids"].split(",")
            oauth2_client = oauth2.GoogleRefreshTokenClient(
                config["oauth_client_id"], config["oauth_client_secret"], config["refresh_token"]
            )
            for customer_id in customer_ids:
                sdk_client = adwords.AdWordsClient(
                    config["developer_token"], oauth2_client, user_agent=config["user_agent"], client_customer_id=customer_id
                )
                selector = {
                    "fields": ["Name", "CanManageClients", "CustomerId", "TestAccount", "DateTimeZone", "CurrencyCode"],
                    "predicates": [
                        {
                            "field": "CustomerId",
                            "operator": "IN",
                            "values": [
                                customer_id,
                            ],
                        }
                    ],
                }
                accounts = self._get_accounts(logger, sdk_client, selector)
                if accounts:
                    account = accounts[0]
                    is_manager = account.canManageClients
                    for stream in streams:
                        if stream.endswith("REPORT") and is_manager:
                            logger.log_by_prefix(f"Unable to sync {stream} with the manager account {customer_id}", "ERROR")
                            sys.exit(1)
                else:
                    err = f"No accounts associated with customer id {customer_id}"
                    logger.log_by_prefix(f"Unable to sync with the provided credentials. Error: {err}", "ERROR")
                    sys.exit(1)
        except Exception as err:
            logger.log_by_prefix(f"Unable to sync. Error: {err}", "ERROR")
            sys.exit(1)

    def check_config(self, logger: AirbyteLogger, config_path: str, config: json) -> AirbyteConnectionStatus:
        # singer catalog that attempts to pull a stream ("accounts") that should always exists, though it may be empty.
        try:
            customer_ids = config["customer_ids"].split(",")
            for customer_id in customer_ids:
                oauth2_client = oauth2.GoogleRefreshTokenClient(
                    config["oauth_client_id"], config["oauth_client_secret"], config["refresh_token"]
                )

                sdk_client = adwords.AdWordsClient(
                    config["developer_token"], oauth2_client, user_agent=config["user_agent"], client_customer_id=customer_id
                )
                selector = {
                    "fields": ["Name", "CanManageClients", "CustomerId", "TestAccount", "DateTimeZone", "CurrencyCode"],
                }
                accounts = self._get_accounts(logger, sdk_client, selector)
                if not accounts:
                    err = f"No accounts associated with customer id {customer_id}"
                    error_msg = f"Unable to connect with the provided credentials. Error: {err}"
                    return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg)
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"{str(e)}")

    def get_sync_mode_overrides(self) -> Dict[str, SyncModeInfo]:
        incremental_streams = [
            "ACCOUNT_PERFORMANCE_REPORT",
            "AD_PERFORMANCE_REPORT",
            "ADGROUP_PERFORMANCE_REPORT",
            "AGE_RANGE_PERFORMANCE_REPORT",
            "AUDIENCE_PERFORMANCE_REPORT",
            "CALL_METRICS_CALL_DETAILS_REPORT",
            "CAMPAIGN_PERFORMANCE_REPORT",
            "CLICK_PERFORMANCE_REPORT",
            "CRITERIA_PERFORMANCE_REPORT",
            "DISPLAY_KEYWORD_PERFORMANCE_REPORT",
            "DISPLAY_TOPICS_PERFORMANCE_REPORT",
            "FINAL_URL_REPORT",
            "GENDER_PERFORMANCE_REPORT",
            "GEO_PERFORMANCE_REPORT",
            "KEYWORDLESS_QUERY_REPORT",
            "KEYWORDS_PERFORMANCE_REPORT",
            "SEARCH_QUERY_PERFORMANCE_REPORT",
            "VIDEO_PERFORMANCE_REPORT",
        ]

        full_refresh_streams = [
            "accounts",
            "ad_groups",
            "campaigns",
            "ads",
            "PLACEHOLDER_FEED_ITEM_REPORT",
            "PLACEMENT_PERFORMANCE_REPORT",
            "SHOPPING_PERFORMANCE_REPORT",
            "PLACEHOLDER_REPORT",
        ]
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
        state_option = f"--state {state_path}" if state_path else ""
        streams = [
            stream["stream"] for stream in self.read_config(catalog_path).get("streams", []) if stream["schema"].get("selected", False)
        ]
        self._check_internal(logger, streams, self.read_config(config_path))
        return f"tap-adwords {config_option} {properties_option} {state_option}"

    def transform_config(self, raw_config):
        # required property in the singer tap, but seems like an implementation detail of stitch
        # https://github.com/singer-io/tap-adwords/blob/cf0c1ff7dae8503f97173a15cf8d78bf975069f8/tap_adwords/__init__.py#L963-L969
        raw_config["user_agent"] = "unknown"
        return raw_config
