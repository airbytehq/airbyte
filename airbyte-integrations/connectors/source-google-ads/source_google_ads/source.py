#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#


from typing import Any, List, Mapping, MutableMapping, Tuple

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.models import AirbyteCatalog, AirbyteStream, SyncMode
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from google.ads.googleads.errors import GoogleAdsException

from .google_ads import GoogleAds
from .streams import (
    AccountPerformanceReport,
    Accounts,
    AdGroupAdReport,
    AdGroupAds,
    AdGroups,
    Campaigns,
    CustomQuery,
    CustomQueryFullRefresh,
    CustomQueryIncremental,
    DisplayKeywordPerformanceReport,
    DisplayTopicsPerformanceReport,
    ShoppingPerformanceReport,
)


class SourceGoogleAds(AbstractSource):
    def get_local_json_schema(self, config) -> MutableMapping[str, Any]:
        """
        As agreed, now it returns the default schema (since read -> schema_generator.py may take hours for the end user).
        If we want to redesign json schema from raw query, this method need to be modified.
        """
        local_json_schema = {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "additionalProperties": True}
        return local_json_schema

    def discover(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteCatalog:
        # streams = [stream.as_airbyte_stream() for stream in self.streams(config=config)]
        streams = []
        for stream in self.streams(config=config):
            if not isinstance(stream, (CustomQueryFullRefresh, CustomQueryIncremental)):
                streams.append(stream.as_airbyte_stream())
        # TODO: extend with custom defined streams
        for usr_query in config.get("custom_query", []):
            local_cursor_field = (
                [usr_query.get("cursor_field")] if isinstance(usr_query.get("cursor_field"), str) else usr_query.get("cursor_field")
            )
            stream = AirbyteStream(
                name=usr_query["table_name"],
                json_schema=self.get_local_json_schema(config=config),
                supported_sync_modes=[SyncMode.full_refresh],
            )
            if usr_query.get("cursor_field"):
                stream.source_defined_cursor = True  # ???
                stream.supported_sync_modes.append(SyncMode.incremental)  # type: ignore
                stream.default_cursor_field = local_cursor_field

            keys = Stream._wrapped_primary_key(usr_query.get("primary_key") or None)  # (!!! read empty strings as null aswell)
            if keys and len(keys) > 0:
                stream.source_defined_primary_key = keys
            streams.append(stream)
        # end of TODO
        return AirbyteCatalog(streams=streams)

    def get_credentials(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        credentials = config["credentials"]

        # https://developers.google.com/google-ads/api/docs/concepts/call-structure#cid
        if "login_customer_id" in config and config["login_customer_id"].strip():
            credentials["login_customer_id"] = config["login_customer_id"]
        return credentials

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, any]:
        try:
            logger.info("Checking the config")
            google_api = GoogleAds(credentials=self.get_credentials(config), customer_id=config["customer_id"])
            account_stream = Accounts(api=google_api)
            list(account_stream.read_records(sync_mode=SyncMode.full_refresh))
            return True, None
        except GoogleAdsException as error:
            return False, f"Unable to connect to Google Ads API with the provided credentials - {repr(error.failure)}"

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        google_api = GoogleAds(credentials=self.get_credentials(config), customer_id=config["customer_id"])
        incremental_stream_config = dict(
            api=google_api, conversion_window_days=config["conversion_window_days"], start_date=config["start_date"]
        )

        custom_query_streams = [
            CustomQuery(custom_query_config=config["custom_query"][i], **incremental_stream_config)
            for i in range(len(config.get("custom_query", [])))
        ]
        return [
            AccountPerformanceReport(**incremental_stream_config),
            DisplayTopicsPerformanceReport(**incremental_stream_config),
            DisplayKeywordPerformanceReport(**incremental_stream_config),
            ShoppingPerformanceReport(**incremental_stream_config),
            AdGroupAdReport(**incremental_stream_config),
            AdGroupAds(api=google_api),
            AdGroups(api=google_api),
            Accounts(api=google_api),
            Campaigns(api=google_api),
        ] + custom_query_streams
