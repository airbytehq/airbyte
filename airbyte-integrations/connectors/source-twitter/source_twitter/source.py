#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
from datetime import date, datetime, timedelta
from typing import Any, Iterator, Mapping, MutableMapping, Optional

from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from twitter_ads.client import Client

from source_twitter.auth import CredentialsCraftAuthenticator
from source_twitter.proxy import set_twitter_proxy
from source_twitter.streams import (
    CampaignsStream,
    LimeItemsStream,
    PromotedTweetBillingMetricsStream,
    PromotedTweetCardsStream,
    PromotedTweetEngagementMetricsStream,
    PromotedTweetLifeTimeValueMobileConversionMetricsStream,
    PromotedTweetMediaMetricsStream,
    PromotedTweetMobileConversionMetricsStream,
    PromotedTweetTweetsStream,
    PromotedTweetVideoMetricsStream,
    PromotedTweetWebConversionMetricsStream,
    PromotedTweetsStream,
)
from source_twitter.types import EndDate, StartDate


class SourceTwitter(AbstractSource):
    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        proxy = config["proxy"]
        set_twitter_proxy(
            protocol=proxy["protocol"], host=proxy["host"], port=proxy["port"], login=proxy["login"], password=proxy["password"]
        )
        return super().check(logger, config)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterator[AirbyteMessage]:
        proxy = config["proxy"]
        set_twitter_proxy(
            protocol=proxy["protocol"], host=proxy["host"], port=proxy["port"], login=proxy["login"], password=proxy["password"]
        )
        return super().read(logger, config, catalog, state)

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> tuple[bool, Optional[str]]:
        # Check dates in config.
        date_from = config.get("date_from")
        date_to = config.get("date_to")
        last_days = config.get("last_days")

        if not (last_days or (date_from and date_to)):
            message = "You must specify either 'Date from' and 'Date to' or just 'Load last N days' params in config."
            return False, message

        if date_from and date_to:
            if datetime.fromisoformat(date_from) > datetime.fromisoformat(date_to):
                return False, "'Date from' exceeds 'Date to'."

        # Check connection to CredentialsCraft.
        auth = self.get_auth(config)
        if isinstance(auth, CredentialsCraftAuthenticator):
            is_success, message = auth.check_connection()
            if not is_success:
                return False, f"Failed to connect to CredentialsCraft: {message}"

        # Check connection to Twitter Ads API.
        credentials = auth()
        twitter_client = Client(
            **credentials,
            options={
                "retry_max": 3,
                "retry_delay": 3000,
                "retry_on_status": [500, 503],
                "retry_on_timeouts": False,
            },
        )
        account_id = config.get("twitter_account_id")
        try:
            twitter_client.accounts(account_id)
        except Exception as e:
            return False, f"Failed to connect to Twitter Ads API: {str(e)}"

        return True, None

    @staticmethod
    def get_auth(config: Mapping[str, Any]) -> CredentialsCraftAuthenticator:
        credentials = config["credentials"]
        auth_type = credentials["auth_type"]
        if auth_type == "credentials_craft_auth":
            return CredentialsCraftAuthenticator(
                host=credentials["credentials_craft_host"],
                bearer_token=credentials["credentials_craft_token"],
                twitter_token_id=credentials["credentials_craft_twitter_token_id"],
            )
        raise ValueError(f"Unknown auth type: '{auth_type}'")

    @staticmethod
    def _prepare_dates(config: Mapping[str, Any]) -> tuple[StartDate, EndDate]:
        date_from = config.get("date_from")
        date_to = config.get("date_to")
        if date_from and date_to:
            return date.fromisoformat(date_from), date.fromisoformat(date_to)

        last_days = config.get("last_days")
        date_from = date.today() - timedelta(days=last_days)
        date_to = date.today() - timedelta(days=1)  # yesterday
        return date_from, date_to

    def streams(self, config: Mapping[str, Any]) -> list[Stream]:
        auth = self.get_auth(config)
        date_from, date_to = self._prepare_dates(config)
        params = {
            "credentials": auth(),
            "date_from": date_from,
            "date_to": date_to,
            "account_id": config["twitter_account_id"],
        }
        return [
            PromotedTweetsStream(**params),
            PromotedTweetEngagementMetricsStream(**params),
            PromotedTweetBillingMetricsStream(**params),
            PromotedTweetVideoMetricsStream(**params),
            PromotedTweetMediaMetricsStream(**params),
            PromotedTweetWebConversionMetricsStream(**params),
            PromotedTweetMobileConversionMetricsStream(**params),
            PromotedTweetLifeTimeValueMobileConversionMetricsStream(**params),
            LimeItemsStream(**params),
            CampaignsStream(**params),
            PromotedTweetTweetsStream(**params),
            PromotedTweetCardsStream(**params),
        ]
