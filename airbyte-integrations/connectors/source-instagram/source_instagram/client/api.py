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

from abc import ABC, abstractmethod
from typing import Any, Dict, Iterator, Sequence, List

import pendulum
from base_python.entrypoint import logger
from facebook_business.adobjects.igmedia import IGMedia
from facebook_business.exceptions import FacebookRequestError


class StreamAPI(ABC):
    result_return_limit = 100

    def __init__(self, api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api

    @abstractmethod
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""


class IncrementalStreamAPI(StreamAPI, ABC):
    @property
    @abstractmethod
    def state_pk(self):
        """Name of the field associated with the state"""

    @property
    def state(self):
        return {self.state_pk: str(self._state)}

    @state.setter
    def state(self, value):
        self._state = pendulum.parse(value[self.state_pk])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = None

    def state_filter(self, record: Dict) -> Dict:
        """Apply state filter to set of records, update cursor(state) if necessary in the end"""
        cursor = pendulum.parse(record[self.state_pk])
        stream_name = self.__class__.__name__
        if stream_name.endswith("API"):
            stream_name = stream_name[:-3]
        logger.info(f"Advancing bookmark for {stream_name} stream from {self._state} to {cursor}")
        self._state = max(cursor, self._state) if self._state else cursor
        return record


class UsersAPI(StreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        yield self._extend_record(self._api.account, fields=fields)

    def _extend_record(self, ig_user, fields) -> Dict:
        return ig_user.api_get(fields=fields).export_all_data()


class UserLifetimeInsightsAPI(StreamAPI):
    LIFETIME_METRICS = ["audience_city", "audience_country", "audience_gender_age", "audience_locale"]
    period = "lifetime"

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        account_id = self._api.account.get("id")
        for insight in self._get_insight_records(params=self._params()):
            yield {
                "id": account_id,
                "metric": insight.get("name"),
                "date": insight.get("values")[0]["end_time"],
                "value": insight.get("values")[0]["value"],
            }

    def _params(self) -> Dict:
        return {"metric": self.LIFETIME_METRICS, "period": self.period}

    def _get_insight_records(self, params) -> Iterator[Any]:
        return self._api.account.get_insights(params=params)


class UserInsightsAPI(IncrementalStreamAPI):
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

    # We can only get User Insights data for today and the previous 29 days.
    # This is Facebook policy
    buffer_days = 29
    days_increment = 1

    def __init__(self, api):
        super().__init__(api=api)
        self._state = api._start_date

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        account_id = self._api.account.get("id")
        for params_per_day in self._params():
            insight_list = []
            for params in params_per_day:
                insight_list += self._get_insight_records(params=params)
            if not insight_list:
                continue

            insight_record = {"id": account_id}
            for insight in insight_list:
                key = (
                    f"{insight.get('name')}_{insight.get('period')}"
                    if insight.get("period") in ["week", "days_28"]
                    else insight.get("name")
                )
                insight_record[key] = insight.get("values")[0]["value"]
                if not insight_record.get("date"):
                    insight_record["date"] = insight.get("values")[0]["end_time"]
            yield self.state_filter(insight_record)

    def _params(self) -> Iterator[List]:
        buffered_start_date = max(self._state.add(minutes=1), pendulum.now().subtract(days=self.buffer_days))
        end_date = pendulum.now()

        while buffered_start_date <= end_date:
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

    def _get_insight_records(self, params):
        return self._api.account.get_insights(params=params)._queue


class MediaAPI(StreamAPI):
    INVALID_CHILDREN_FIELDS = ["caption", "comments_count", "is_comment_enabled", "like_count", "children"]

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        children_fields = list(set(fields) - set(self.INVALID_CHILDREN_FIELDS))
        media = self._get_media({"limit": self.result_return_limit}, fields)
        for record in media:
            record_data = record.export_all_data()
            if record_data.get("children"):
                record_data["children"] = [
                    self._get_single_record(child_record["id"], children_fields).export_all_data()
                    for child_record in record.get("children")["data"]
                ]
            yield record_data

    def _get_media(self, params, fields) -> Iterator[Any]:
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        return self._api.account.get_media(params=params, fields=fields)

    def _get_single_record(self, media_id, fields) -> IGMedia:
        return IGMedia(media_id).api_get(fields=fields)


class StoriesAPI(StreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        media = self._get_stories({"limit": self.result_return_limit}, fields)
        for record in media:
            record_data = record.export_all_data()
            yield record_data

    def _get_stories(self, params, fields: list) -> Iterator[Any]:
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        return self._api.account.get_stories(params=params, fields=fields)


class MediaInsightsAPI(MediaAPI):
    MEDIA_METRICS = ["engagement", "impressions", "reach", "saved"]
    CAROUSEL_ALBUM_METRICS = ["carousel_album_engagement", "carousel_album_impressions", "carousel_album_reach", "carousel_album_saved"]

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        media = self._get_media({"limit": self.result_return_limit}, ["media_type"])
        for ig_media in media:
            yield {
                **{"id": ig_media.get("id")},
                **{record.get("name"): record.get("values")[0]["value"] for record in self._get_insights(ig_media)},
            }

    def _get_insights(self, item) -> Iterator[Any]:
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

        # An error might occur if the media was posted before the most recent time that
        # the user's account was converted to a business account from a personal account
        try:
            return item.get_insights(params={"metric": metrics})
        except FacebookRequestError as error:
            logger.error(f"Insights error: {error.body()}")
            raise error


class StoriesInsightsAPI(StoriesAPI):
    STORY_METRICS = ["exits", "impressions", "reach", "replies", "taps_forward", "taps_back"]

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        stories = self._get_stories({"limit": self.result_return_limit}, fields=[])
        for ig_story in stories:
            insights = self._get_insights(ig_story)
            if insights:
                yield {
                    **{"id": ig_story.get("id")},
                    **{record.get("name"): record.get("values")[0]["value"] for record in insights},
                }

    def _get_insights(self, item) -> Iterator[Any]:
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """

        # Story IG Media object metrics with values less than 5 will return an error code 10 with the message (#10)
        # Not enough viewers for the media to show insights.
        try:
            return item.get_insights(params={"metric": self.STORY_METRICS})
        except FacebookRequestError as error:
            logger.error(f"Insights error: {error.api_error_message()}")
            if error.api_error_code() == 10:
                return []
            raise error
