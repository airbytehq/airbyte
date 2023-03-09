#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import copy
from abc import ABC
from datetime import datetime
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from cached_property import cached_property
from facebook_business.adobjects.igmedia import IGMedia
from facebook_business.exceptions import FacebookRequestError
from source_instagram.api import InstagramAPI

from .common import remove_params_from_url


class InstagramStream(Stream, ABC):
    """Base stream class"""

    page_size = 100
    primary_key = "id"

    def __init__(self, api: InstagramAPI, **kwargs):
        super().__init__(**kwargs)
        self._api = api

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        non_object_fields = ["page_id", "business_account_id"]
        fields = list(self.get_json_schema().get("properties", {}).keys())
        return list(set(fields) - set(non_object_fields))

    def request_params(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """Parameters that should be passed to query_records method"""
        return {"limit": self.page_size}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override to define the slices for this stream. See the stream slicing section of the docs for more information.

        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return:
        """
        for account in self._api.accounts:
            yield {"account": account}

    def transform(self, record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        return self._clear_url(record)

    @staticmethod
    def _clear_url(record: MutableMapping[str, Any]) -> MutableMapping[str, Any]:
        """
        This function removes the _nc_rid parameter from the video url and ccb from profile_picture_url for users.
        _nc_rid is generated every time a new one and ccb can change its value, and tests fail when checking for identity.
        This does not spoil the link, it remains correct and by clicking on it you can view the video or see picture.
        """
        if record.get("media_url"):
            record["media_url"] = remove_params_from_url(record["media_url"], params=["_nc_rid"])
        if record.get("profile_picture_url"):
            record["profile_picture_url"] = remove_params_from_url(record["profile_picture_url"], params=["ccb"])

        return record


class InstagramIncrementalStream(InstagramStream, ABC):
    """Base class for incremental streams"""

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.instance(start_date)


class Users(InstagramStream):
    """Docs: https://developers.facebook.com/docs/instagram-api/reference/ig-user"""

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        account = stream_slice["account"]
        ig_account = account["instagram_business_account"]
        record = ig_account.api_get(fields=self.fields).export_all_data()
        record["page_id"] = account["page_id"]
        yield self.transform(record)


class UserLifetimeInsights(InstagramStream):
    """Docs: https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights"""

    primary_key = None
    LIFETIME_METRICS = ["audience_city", "audience_country", "audience_gender_age", "audience_locale"]
    period = "lifetime"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        account = stream_slice["account"]
        ig_account = account["instagram_business_account"]
        for insight in ig_account.get_insights(params=self.request_params()):
            yield {
                "page_id": account["page_id"],
                "business_account_id": ig_account.get("id"),
                "metric": insight["name"],
                "date": insight["values"][0]["end_time"],
                "value": insight["values"][0]["value"],
            }

    def request_params(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = super().request_params(stream_slice=stream_slice, stream_state=stream_state)
        params.update({"metric": self.LIFETIME_METRICS, "period": self.period})
        return params


class UserInsights(InstagramIncrementalStream):
    """Docs: https://developers.facebook.com/docs/instagram-api/reference/ig-user/insights"""

    METRICS_BY_PERIOD = {
        "day": [
            "email_contacts",
            "follower_count",
            "get_directions_clicks",
            "impressions",
            "phone_call_clicks",
            "profile_views",
            "reach",
            "text_message_clicks",
            "website_clicks",
        ],
        "week": ["impressions", "reach"],
        "days_28": ["impressions", "reach"],
        "lifetime": ["online_followers"],
    }

    primary_key = None
    cursor_field = "date"

    # For some metrics we can only get insights not older than 30 days, it is Facebook policy
    buffer_days = 30
    days_increment = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._end_date = pendulum.now()

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        account = stream_slice["account"]
        ig_account = account["instagram_business_account"]
        account_id = ig_account.get("id")

        base_params = self.request_params(stream_state=stream_state, stream_slice=stream_slice)
        insight_list = []
        # iterate over each period, query insights
        for period, metrics in self.METRICS_BY_PERIOD.items():
            params = {
                **base_params,
                "metric": metrics,
                "period": [period],
            }

            # we get only first record, because cursor will try to fetch next date interval
            cursor = ig_account.get_insights(params=params)
            if len(cursor):
                insight_list += [insights.export_all_data() for insights in cursor[: len(cursor)]]

        # end then merge all periods in one record
        insight_record = {"page_id": account["page_id"], "business_account_id": account_id}
        for insight in insight_list:
            key = insight["name"]
            if insight["period"] in ["week", "days_28"]:
                key += f"_{insight['period']}"

            insight_record[key] = insight.get("values")[0]["value"]  # this depends on days_increment value
            if not insight_record.get(self.cursor_field):
                insight_record[self.cursor_field] = insight.get("values")[0]["end_time"]

        yield insight_record

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """Extend default slicing based on accounts with slices based on date intervals"""
        stream_state = stream_state or {}
        stream_slices = super().stream_slices(sync_mode=sync_mode, cursor_field=cursor_field, stream_state=stream_state)
        for stream_slice in stream_slices:
            account = stream_slice["account"]
            account_id = account["instagram_business_account"]["id"]

            state_value = stream_state.get(account_id, {}).get(self.cursor_field)
            start_date = pendulum.parse(state_value) if state_value else self._start_date
            start_date = max(start_date, self._start_date, pendulum.now().subtract(days=self.buffer_days))
            if start_date > pendulum.now():
                continue
            for since in pendulum.period(start_date, self._end_date).range("days", self.days_increment):
                until = since.add(days=self.days_increment)
                self.logger.info(f"Reading insights between {since.date()} and {until.date()}")
                yield {
                    **stream_slice,
                    "since": since.to_datetime_string(),
                    "until": until.to_datetime_string(),  # excluding
                }

    def request_params(
        self,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        """Append datetime range params"""
        params = super().request_params(stream_state=stream_state, stream_slice=stream_slice)
        return {
            **params,
            "since": stream_slice["since"],
            "until": stream_slice["until"],
        }

    def _state_has_legacy_format(self, state: Mapping[str, Any]) -> bool:
        """Tell if the format of state is outdated"""
        for value in state.values():
            if not isinstance(value, Mapping):
                return True
        return False

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """Update stream state from latest record"""
        record_value = latest_record[self.cursor_field]
        account_id = latest_record.get("business_account_id")
        state_value = current_stream_state.get(account_id, {}).get(self.cursor_field) or record_value
        max_cursor = max(pendulum.parse(state_value), pendulum.parse(record_value))

        new_stream_state = copy.deepcopy(current_stream_state)
        new_stream_state[account_id] = {
            self.cursor_field: str(max_cursor),
        }

        return new_stream_state


class Media(InstagramStream):
    """Children objects can only be of the media_type == "CAROUSEL_ALBUM".
    And children object does not support INVALID_CHILDREN_FIELDS fields,
    so they are excluded when trying to get child objects to avoid the error
    """

    INVALID_CHILDREN_FIELDS = ["caption", "comments_count", "is_comment_enabled", "like_count", "children"]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        """
        This method should be overridden by subclasses to read records based on the inputs
        """
        account = stream_slice["account"]
        ig_account = account["instagram_business_account"]
        media = ig_account.get_media(params=self.request_params(), fields=self.fields)
        for record in media:
            record_data = record.export_all_data()
            if record_data.get("children"):
                ids = [child["id"] for child in record["children"]["data"]]
                record_data["children"] = list(self._get_children(ids))

            record_data.update(
                {
                    "page_id": account["page_id"],
                    "business_account_id": ig_account.get("id"),
                }
            )
            yield self.transform(record_data)

    def _get_children(self, ids: List):
        children_fields = list(set(self.fields) - set(self.INVALID_CHILDREN_FIELDS))
        for pk in ids:
            yield self.transform(IGMedia(pk).api_get(fields=children_fields).export_all_data())


class MediaInsights(Media):
    """Docs: https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights"""

    MEDIA_METRICS = ["engagement", "impressions", "reach", "saved"]
    CAROUSEL_ALBUM_METRICS = ["carousel_album_engagement", "carousel_album_impressions", "carousel_album_reach", "carousel_album_saved"]
    REELS_METRICS = ["comments", "likes", "reach", "saved", "shares", "total_interactions", "plays"]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        account = stream_slice["account"]
        ig_account = account["instagram_business_account"]
        media = ig_account.get_media(params=self.request_params(), fields=["media_type", "media_product_type"])
        for ig_media in media:
            account_id = ig_account.get("id")
            insights = self._get_insights(ig_media, account_id)
            if insights is None:
                break

            insights["id"] = ig_media["id"]
            insights["page_id"] = account["page_id"]
            insights["business_account_id"] = ig_account["id"]
            yield self.transform(insights)

    def _get_insights(self, item, account_id) -> Optional[MutableMapping[str, Any]]:
        """Get insights for specific media"""
        if item.get("media_product_type") == "REELS":
            metrics = self.REELS_METRICS
        elif item.get("media_type") == "VIDEO":
            metrics = self.MEDIA_METRICS + ["video_views"]
        elif item.get("media_type") == "CAROUSEL_ALBUM":
            metrics = self.CAROUSEL_ALBUM_METRICS

        else:
            metrics = self.MEDIA_METRICS

        try:
            insights = item.get_insights(params={"metric": metrics})
            return {record.get("name"): record.get("values")[0]["value"] for record in insights}
        except FacebookRequestError as error:
            # An error might occur if the media was posted before the most recent time that
            # the user's account was converted to a business account from a personal account
            if error.api_error_subcode() == 2108006:
                details = error.body().get("error", {}).get("error_user_title") or error.api_error_message()
                self.logger.error(f"Insights error for business_account_id {account_id}: {details}")
                # We receive all Media starting from the last one, and if on the next Media we get an Insight error,
                # then no reason to make inquiries for each Media further, since they were published even earlier.
                return None
            raise error


class Stories(InstagramStream):
    """Docs: https://developers.facebook.com/docs/instagram-api/reference/ig-user/stories"""

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        account = stream_slice["account"]
        ig_account = account["instagram_business_account"]
        stories = ig_account.get_stories(params=self.request_params(), fields=self.fields)
        for record in stories:
            record_data = record.export_all_data()
            record_data["page_id"] = account["page_id"]
            record_data["business_account_id"] = ig_account.get("id")
            yield self.transform(record_data)


class StoryInsights(Stories):
    """Docs: https://developers.facebook.com/docs/instagram-api/reference/ig-media/insights"""

    metrics = ["exits", "impressions", "reach", "replies", "taps_forward", "taps_back"]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        account = stream_slice["account"]
        ig_account = account["instagram_business_account"]
        stories = ig_account.get_stories(params=self.request_params(), fields=[])
        for ig_story in stories:
            insights = self._get_insights(IGMedia(ig_story["id"]))
            if not insights:
                continue

            insights["id"] = ig_story["id"]
            insights["page_id"] = account["page_id"]
            insights["business_account_id"] = ig_account["id"]
            yield self.transform(insights)

    def _get_insights(self, story: IGMedia) -> MutableMapping[str, Any]:
        """Get insights for specific story"""

        # Story IG Media object metrics with values less than 5 will return an error code 10 with the message (#10)
        # Not enough viewers for the media to show insights.
        try:
            insights = story.get_insights(params={"metric": self.metrics})
            return {record["name"]: record["values"][0]["value"] for record in insights}
        except FacebookRequestError as error:
            if error.api_error_code() == 10:
                self.logger.error(f"Insights error: {error.api_error_message()}")
                return {}
            raise error
