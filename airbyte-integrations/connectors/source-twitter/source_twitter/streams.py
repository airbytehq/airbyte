from abc import ABC
from datetime import date, datetime, timedelta
from typing import Any, Iterable, List, Mapping, Optional, Type

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from twitter_ads.account import Account
from twitter_ads.campaign import Campaign, LineItem
from twitter_ads.client import Client
from twitter_ads.creative import Card, PromotedTweet, Tweets
from twitter_ads.enum import GRANULARITY, METRIC_GROUP, PLACEMENT, TWEET_TYPE
from twitter_ads.utils import split_list

from source_twitter.schemas import (
    Campaigns,
    LineItems,
    PromotedTweetBillingMetrics,
    PromotedTweetCards,
    PromotedTweetEngagementMetrics,
    PromotedTweetLifeTimeValueMobileConversion,
    PromotedTweetMediaMetrics,
    PromotedTweetMobileConversionMetrics,
    PromotedTweetTweets,
    PromotedTweetVideoMetrics,
    PromotedTweetWebConversionMetrics,
    PromotedTweets,
)
from source_twitter.types import SchemaT, TwitterCredentials


class TwitterAdsStream(Stream, ABC):
    def __init__(self, credentials: TwitterCredentials, date_from: date, date_to: date, account_id: str):
        self.credentials = credentials
        self.date_from = date_from
        self.date_to = date_to
        self.account_id = account_id
        self._account: Optional[Account] = None
        self._client: Optional[Client] = None
        self.create_client()

    def create_client(self) -> None:
        self._client = Client(
            **self.credentials,
            options={
                "retry_max": 3,
                "retry_delay": 3000,
                "retry_on_status": [500, 503],
                "retry_on_timeouts": True,
            },
        )

    def fetch_account(self) -> None:
        self._account = self._client.accounts(self.account_id)

    @property
    def datetime_from(self) -> datetime:
        return datetime.fromordinal(self.date_from.toordinal())

    @property
    def datetime_to(self) -> datetime:
        return datetime.fromordinal(self.date_to.toordinal()) + timedelta(days=1)


class ActiveEntityStream(TwitterAdsStream, ABC):
    @property
    def twitter_ads_entity_class(self):
        raise NotImplementedError

    @property
    def schema_class(self) -> Type[SchemaT]:
        raise NotImplementedError

    @property
    def filter_by_id_param(self) -> str:
        raise NotImplementedError

    @property
    def primary_key(self) -> None:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.schema_class.schema()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.fetch_account()
        active_entities = self.twitter_ads_entity_class.active_entities(
            account=self._account, start_time=self.datetime_from, end_time=self.datetime_to
        )
        ids = [active_entity["entity_id"] for active_entity in active_entities]
        for chunk_ids in split_list(ids, 200):
            params = {
                "account": self._account,
                self.filter_by_id_param: ",".join(chunk_ids),
                "with_deleted": True,
            }
            entities = self.twitter_ads_entity_class.all(**params)
            for entity in entities:
                data = {key: getattr(entity, key, None) for key in self.schema_class.__fields__.keys()}
                yield self.schema_class(**data).dict()


class PromotedTweetsStream(ActiveEntityStream):
    @property
    def twitter_ads_entity_class(self):
        return PromotedTweet

    @property
    def schema_class(self) -> Type[SchemaT]:
        return PromotedTweets

    @property
    def filter_by_id_param(self) -> str:
        return "promoted_tweet_ids"


class PromotedTweetMetricsStream(TwitterAdsStream, ABC):
    @property
    def metric_group(self) -> METRIC_GROUP:
        raise NotImplementedError

    @property
    def schema_class(self) -> Type[SchemaT]:
        raise NotImplementedError

    @property
    def date_period(self) -> list[date]:
        if self.date_from == self.date_to:
            return [self.date_from]
        return [self.date_from + timedelta(days=i) for i in range((self.date_to - self.date_from).days + 1)]

    def _get_active_entities_ids(self) -> list[str]:
        entities = PromotedTweet.active_entities(account=self._account, start_time=self.datetime_from, end_time=self.datetime_to)
        return [entity["entity_id"] for entity in entities]

    def _get_metrics_by_date(self, date_sequence_number: int, metrics: dict) -> dict:
        data = {}
        for metric, value in metrics.items():
            if isinstance(value, list):
                try:
                    data[metric] = value[date_sequence_number]
                except IndexError:
                    data[metric] = None
            elif isinstance(value, dict):
                data[metric] = self._get_metrics_by_date(date_sequence_number, value)
            else:
                data[metric] = None
        return data

    @property
    def primary_key(self) -> None:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return self.schema_class.schema()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.fetch_account()
        ids = self._get_active_entities_ids()
        for chunk_ids in split_list(ids, 20):
            stats = PromotedTweet.all_stats(
                self._account,
                chunk_ids,
                metric_groups=[self.metric_group],
                granularity=GRANULARITY.DAY,
                placement=PLACEMENT.ALL_ON_TWITTER,
                start_time=self.datetime_from,
                end_time=self.datetime_to,
            )
            for stat in stats:
                promoted_tweet_id = stat["id"]
                promoted_tweet_metrics = stat["id_data"][0]["metrics"]
                for i, date_ in enumerate(self.date_period):
                    metrics = self._get_metrics_by_date(date_sequence_number=i, metrics=promoted_tweet_metrics)
                    yield self.schema_class(promoted_tweet_id=promoted_tweet_id, date=date_, **metrics).dict()


class PromotedTweetEngagementMetricsStream(PromotedTweetMetricsStream):
    @property
    def metric_group(self) -> METRIC_GROUP:
        return METRIC_GROUP.ENGAGEMENT

    @property
    def schema_class(self) -> Type[SchemaT]:
        return PromotedTweetEngagementMetrics


class PromotedTweetBillingMetricsStream(PromotedTweetMetricsStream):
    @property
    def metric_group(self) -> METRIC_GROUP:
        return METRIC_GROUP.BILLING

    @property
    def schema_class(self) -> Type[SchemaT]:
        return PromotedTweetBillingMetrics


class PromotedTweetVideoMetricsStream(PromotedTweetMetricsStream):
    @property
    def metric_group(self) -> METRIC_GROUP:
        return METRIC_GROUP.VIDEO

    @property
    def schema_class(self) -> Type[SchemaT]:
        return PromotedTweetVideoMetrics


class PromotedTweetMediaMetricsStream(PromotedTweetMetricsStream):
    @property
    def metric_group(self) -> METRIC_GROUP:
        return METRIC_GROUP.MEDIA

    @property
    def schema_class(self) -> Type[SchemaT]:
        return PromotedTweetMediaMetrics


class PromotedTweetWebConversionMetricsStream(PromotedTweetMetricsStream):
    @property
    def metric_group(self) -> METRIC_GROUP:
        return METRIC_GROUP.WEB_CONVERSION

    @property
    def schema_class(self) -> Type[SchemaT]:
        return PromotedTweetWebConversionMetrics


class PromotedTweetMobileConversionMetricsStream(PromotedTweetMetricsStream):
    @property
    def metric_group(self) -> METRIC_GROUP:
        return METRIC_GROUP.MOBILE_CONVERSION

    @property
    def schema_class(self) -> Type[SchemaT]:
        return PromotedTweetMobileConversionMetrics


class PromotedTweetLifeTimeValueMobileConversionMetricsStream(PromotedTweetMetricsStream):
    @property
    def metric_group(self) -> METRIC_GROUP:
        return METRIC_GROUP.LIFE_TIME_VALUE_MOBILE_CONVERSION

    @property
    def schema_class(self) -> Type[SchemaT]:
        return PromotedTweetLifeTimeValueMobileConversion


class LimeItemsStream(ActiveEntityStream):
    @property
    def twitter_ads_entity_class(self):
        return LineItem

    @property
    def schema_class(self) -> Type[SchemaT]:
        return LineItems

    @property
    def filter_by_id_param(self) -> str:
        return "line_item_ids"


class CampaignsStream(ActiveEntityStream):
    @property
    def twitter_ads_entity_class(self):
        return Campaign

    @property
    def schema_class(self) -> Type[SchemaT]:
        return Campaigns

    @property
    def filter_by_id_param(self) -> str:
        return "campaign_ids"


class PromotedTweetTweetsStream(TwitterAdsStream):
    @property
    def primary_key(self) -> None:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return PromotedTweetTweets.schema()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.fetch_account()

        # Fetch PromotedTweets active entities.
        active_entities = PromotedTweet.active_entities(account=self._account, start_time=self.datetime_from, end_time=self.datetime_to)
        active_entities_ids = [active_entity["entity_id"] for active_entity in active_entities]

        # Fetch PromotedTweets.
        tweet_ids = []
        for chunk_ids in split_list(active_entities_ids, 200):
            params = {
                "account": self._account,
                "promoted_tweet_ids": ",".join(chunk_ids),
                "with_deleted": True,
            }
            promoted_tweets = PromotedTweet.all(**params)
            for promoted_tweet in promoted_tweets:
                tweet_ids.append(promoted_tweet.tweet_id)

        # Fetch Tweets.
        for chunk_ids in split_list(tweet_ids, 200):
            ids = ",".join(chunk_ids)
            tweets = Tweets.all(self._account, tweet_ids=ids, tweet_type=TWEET_TYPE.PUBLISHED)
            for tweet in tweets:
                user_id = tweet["user"]["id"]
                yield PromotedTweetTweets(user_id=user_id, **tweet).dict()


class PromotedTweetCardsStream(TwitterAdsStream):
    @property
    def primary_key(self) -> None:
        return None

    def get_json_schema(self) -> Mapping[str, Any]:
        return PromotedTweetCards.schema()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        self.fetch_account()

        # Fetch PromotedTweets active entities.
        active_entities = PromotedTweet.active_entities(account=self._account, start_time=self.datetime_from, end_time=self.datetime_to)
        active_entities_ids = [active_entity["entity_id"] for active_entity in active_entities]

        # Fetch PromotedTweets.
        tweet_ids = []
        for chunk_ids in split_list(active_entities_ids, 200):
            params = {
                "account": self._account,
                "promoted_tweet_ids": ",".join(chunk_ids),
                "with_deleted": True,
            }
            promoted_tweets = PromotedTweet.all(**params)
            for promoted_tweet in promoted_tweets:
                tweet_ids.append(promoted_tweet.tweet_id)

        # Fetch Tweets.
        card_uris = []
        for chunk_ids in split_list(tweet_ids, 200):
            ids = ",".join(chunk_ids)
            tweets = Tweets.all(self._account, tweet_ids=ids, tweet_type=TWEET_TYPE.PUBLISHED)
            for tweet in tweets:
                if card_uri := tweet.get("card_uri"):
                    card_uris.append(card_uri)

        # Fetch Cards.
        for chunk_ids in split_list(card_uris, 200):
            ids = ",".join(chunk_ids)
            cards = Card.all(account=self._account, card_uris=ids)
            for card in cards:
                data = {key: getattr(card, key, None) for key in PromotedTweetCards.__fields__.keys()}
                yield PromotedTweetCards(**data).dict()
