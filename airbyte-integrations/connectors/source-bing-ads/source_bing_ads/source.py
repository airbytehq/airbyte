#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, List, Mapping, Optional, Tuple

from airbyte_cdk import TState, YamlDeclarativeSource
from airbyte_cdk.models import ConfiguredAirbyteCatalog, FailureType, SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.utils import AirbyteTracedException
from source_bing_ads.base_streams import Accounts
from source_bing_ads.client import Client
from source_bing_ads.report_streams import (  # noqa: F401
    BingAdsReportingServiceStream,
)


class SourceBingAds(YamlDeclarativeSource):
    """
    Source implementation of Bing Ads API. Fetches advertising data from accounts
    """

    def __init__(self, catalog: Optional[ConfiguredAirbyteCatalog], config: Optional[Mapping[str, Any]], state: TState, **kwargs):
        super().__init__(catalog=catalog, config=config, state=state, **{"path_to_yaml": "manifest.yaml"})

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Any]:
        try:
            client = Client(**config)
            accounts = Accounts(client, config)
            account_ids = set()
            for _slice in accounts.stream_slices():
                account_ids.update({str(account["Id"]) for account in accounts.read_records(SyncMode.full_refresh, _slice)})
            if account_ids:
                return True, None
            else:
                raise AirbyteTracedException(
                    message="Config validation error: You don't have accounts assigned to this user. Please verify your developer token.",
                    internal_message="You don't have accounts assigned to this user.",
                    failure_type=FailureType.config_error,
                )
        except Exception as error:
            return False, error

    def _clear_reporting_object_name(self, report_object: str) -> str:
        # reporting mixin adds it
        if report_object.endswith("Request"):
            return report_object.replace("Request", "")
        return report_object
