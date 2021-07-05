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

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Sequence, MutableMapping, Iterable, Mapping

import pendulum
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from cached_property import cached_property
from facebook_business.adobjects.igmedia import IGMedia
from facebook_business.adobjects.iguser import IGUser
from facebook_business.exceptions import FacebookRequestError
from source_instagram.api import API

from .common import remove_params_from_url


class InstagramStream(Stream, ABC):
    """Base stream class"""

    page_size = 100
    primary_key = "id"

    def __init__(self, api: API, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api

    @cached_property
    def fields(self) -> List[str]:
        """List of fields that we want to query, for now just all properties from stream's schema"""
        non_object_fields = ["page_id", "business_account_id"]
        fields = list(self.get_json_schema().get("properties", {}).keys())
        return list(set(fields) - set(non_object_fields))

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        """Parameters that should be passed to query_records method"""
        return {"limit": self.page_size}

    def stream_slices(
        self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        """
        Override to define the slices for this stream. See the stream slicing section of the docs for more information.

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
    """TODO"""
    cursor_field = "updated_time"

    def __init__(self, start_date: datetime, **kwargs):
        super().__init__(**kwargs)
        self._start_date = pendulum.instance(start_date)

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]):
        """Update stream state from latest record"""
        record_value = latest_record[self.cursor_field]
        state_value = current_stream_state.get(self.cursor_field) or record_value
        max_cursor = max(pendulum.parse(state_value), pendulum.parse(record_value))

        return {
            self.cursor_field: str(max_cursor),
        }


class Users(InstagramStream):
    """TODO"""
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        account = stream_slice["account"]
        record = account["instagram_business_account"].api_get(fields=self.fields).export_all_data()
        record["page_id"] = account["page_id"]
        yield record


class UserLifetimeInsights(InstagramStream):
    """TODO"""
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
        for insight in account["instagram_business_account"].get_insights(params=self.request_params()):
            yield {
                "page_id": account["page_id"],
                "business_account_id": account["instagram_business_account"].get("id"),
                "metric": insight["name"],
                "date": insight["values"][0]["end_time"],
                "value": insight["values"][0]["value"],
            }

    def request_params(self, **kwargs) -> MutableMapping[str, Any]:
        params = super().request_params(**kwargs)
        params.update({"metric": self.LIFETIME_METRICS, "period": self.period})
        return params


class UserInsights(InstagramIncrementalStream):
    """TODO"""
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

    state_pk = "date"
    cursor_field = "business_account_id"

    # We can only get User Insights data for today and the previous 29 days.
    # This is Facebook policy
    buffer_days = 29
    days_increment = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._end_date = pendulum.now()

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        for account in self._api.accounts:
            account_id = account["instagram_business_account"].get("id")
            self._set_state(account_id)
            for params_per_day in self._params(account_id):
                insight_list = []
                for params in params_per_day:
                    insight_list += account["instagram_business_account"].get_insights(params=params)._queue
                if not insight_list:
                    continue

                insight_record = {"page_id": account["page_id"], "business_account_id": account_id}
                for insight in insight_list:
                    key = (
                        f"{insight.get('name')}_{insight.get('period')}"
                        if insight.get("period") in ["week", "days_28"]
                        else insight.get("name")
                    )
                    insight_record[key] = insight.get("values")[0]["value"]
                    if not insight_record.get("date"):
                        insight_record["date"] = insight.get("values")[0]["end_time"]

                yield record

    def _params(self, account_id: str) -> Iterator[List]:

        buffered_start_date = self._state[account_id]

        while buffered_start_date <= self._end_date:
            params_list = []
            for period, metrics in self.METRICS_BY_PERIOD.items():
                params_list.append(
                    {
                        "metric": metrics,
                        "period": [period],
                        "since": buffered_start_date.to_datetime_string(),
                        "until": buffered_start_date.add(days=self.days_increment).to_datetime_string(),
                    }
                )
            yield params_list
            buffered_start_date = buffered_start_date.add(days=self.days_increment)

    def _set_state(self, account_id: str):
        start_date = self._state[account_id] if self._state.get(account_id) else self._api._start_date
        self._state[account_id] = max(start_date, pendulum.now().subtract(days=self.buffer_days))


class Media(InstagramStream):
    """ Children objects can only be of the media_type == "CAROUSEL_ALBUM".
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
        account = stream_slice['account']
        params = self.request_params()
        media = account["instagram_business_account"].get_media(params=params, fields=self.fields)
        for record in media:
            record_data = record.export_all_data()
            if record_data.get("children"):
                ids = [child["id"] for child in record["children"]["data"]]
                record_data["children"] = list(self._get_children(ids))

            record_data.update(
                {
                    "page_id": account["page_id"],
                    "business_account_id": account["instagram_business_account"].get("id"),
                }
            )
            yield self.transform(record_data)

    def _get_children(self, ids: List):
        children_fields = list(set(self.fields) - set(self.INVALID_CHILDREN_FIELDS))
        for pk in ids:
            yield self.transform(IGMedia(pk).api_get(fields=children_fields))


class MediaInsights(Media):
    """TODO"""

    MEDIA_METRICS = ["engagement", "impressions", "reach", "saved"]
    CAROUSEL_ALBUM_METRICS = ["carousel_album_engagement", "carousel_album_impressions", "carousel_album_reach", "carousel_album_saved"]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        account = stream_slice['account']
        ig_account = account["instagram_business_account"]
        media = self._get_media(ig_account, self.request_params(), ["media_type"])
        for ig_media in media:
            account_id = ig_account.get("id")
            media_insights = self._get_insights(ig_media, account_id)
            if media_insights is None:
                break
            yield {
                "id": ig_media.get("id"),
                "page_id": account["page_id"],
                "business_account_id": account_id,
                **{record.get("name"): record.get("values")[0]["value"] for record in media_insights},
            }

    def _get_insights(self, item, account_id) -> Optional[Iterator[Any]]:
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        if item.get("media_type") == "VIDEO":
            metrics = self.MEDIA_METRICS + ["video_views"]
        elif item.get("media_type") == "CAROUSEL_ALBUM":
            metrics = self.CAROUSEL_ALBUM_METRICS
        else:
            metrics = self.MEDIA_METRICS

        try:
            return item.get_insights(params={"metric": metrics})
        except FacebookRequestError as error:
            # An error might occur if the media was posted before the most recent time that
            # the user's account was converted to a business account from a personal account
            if error.api_error_subcode() == 2108006:
                self.logger.error(f"Insights error for business_account_id {account_id}: {error.body()}")

                # We receive all Media starting from the last one, and if on the next Media we get an Insight error,
                # then no reason to make inquiries for each Media further, since they were published even earlier.
                return None
            raise error


class Stories(InstagramStream):
    """TODO"""

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:

        for account in self._api.accounts:
            stories = self._get_stories(account["instagram_business_account"], params=self.request_params())
            for record in stories:
                record_data = record.export_all_data()
                record_data["page_id"] = account["page_id"]
                record_data["business_account_id"] = account["instagram_business_account"].get("id")
                yield self._clear_url(record_data)

    def _get_stories(self, instagram_user: IGUser, params: Mapping, fields: Sequence[str] = None) -> Iterator[Any]:
        yield from instagram_user.get_stories(params=params, fields=fields)


class StoriesInsights(Stories):
    """TODO"""

    metrics = ["exits", "impressions", "reach", "replies", "taps_forward", "taps_back"]

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:

        for ig_story in stories.read_records():
            insights = self._get_insights(IGMedia(ig_story["id"]))
            if insights:
                yield {
                    "id": ig_story["id"],
                    "page_id": ig_story["page_id"],
                    "business_account_id": ig_story["business_account_id"],
                    ** {record["name"]: record["values"][0]["value"] for record in insights},
                }

    def _get_insights(self, item: IGMedia) -> Iterator[Any]:
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """

        # Story IG Media object metrics with values less than 5 will return an error code 10 with the message (#10)
        # Not enough viewers for the media to show insights.
        try:
            return item.get_insights(params={"metric": self.metrics})
        except FacebookRequestError as error:
            self.logger.error(f"Insights error: {error.api_error_message()}")
            if error.api_error_code() == 10:
                return []
            raise error
