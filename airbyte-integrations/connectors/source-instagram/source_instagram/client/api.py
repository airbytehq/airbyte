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
from typing import Iterator, Sequence

from base_python.entrypoint import logger
from facebook_business.exceptions import FacebookRequestError


class StreamAPI(ABC):
    result_return_limit = 100

    def __init__(self, api, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._api = api

    @abstractmethod
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Iterate over entities"""


class IgUsersAPI(StreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        yield self._extend_record(self._api.account, fields=fields)

    def _extend_record(self, ig_user, fields):
        return ig_user.api_get(fields=fields).export_all_data()


class IgUserInsightsAPI(StreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        for params in self._params():
            yield from (insight.export_all_data() for insight in self._api.account.get_insights(params=params))

    def _params(self):
        period_dicts = {
            "lifetime": ["audience_city", "audience_country", "audience_gender_age", "audience_locale", "online_followers"],
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
        }
        for period, metrics in period_dicts.items():
            yield {"metric": metrics, "period": [period]}


class IgMediaAPI(StreamAPI):
    def __init__(self, api, method: str = None, *args, **kwargs):
        super().__init__(api, *args, **kwargs)
        self._method = method

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        media = self._get_records({"limit": self.result_return_limit}, fields)
        for record in media:
            yield record.export_all_data()

    def _get_records(self, params, fields):
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        return getattr(self._api.account, self._method)(params=params, fields=fields)


class IgMediaInsightsAPI(IgMediaAPI):
    media_metrics = ["engagement", "impressions", "reach", "saved"]
    story_metrics = ["exits", "impressions", "reach", "replies", "taps_forward", "taps_back"]

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        media = self._get_records({"limit": self.result_return_limit}, ["media_type"])
        for ig_media in media:
            yield from (record.export_all_data() for record in self._get_insights(ig_media))

    def _get_insights(self, item):
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        if self._method == "get_media":
            metrics = self.media_metrics + ["video_views"] if item.get("media_type") == "VIDEO" else self.media_metrics
        else:
            metrics = self.story_metrics

        # An error might occur if the media was posted before the most recent time that the user's account was converted to a business account from a personal account
        try:
            return item.get_insights(params={"metric": metrics})
        except FacebookRequestError as e:
            logger.error(f"Insights error: {e.body()}")
            return []
