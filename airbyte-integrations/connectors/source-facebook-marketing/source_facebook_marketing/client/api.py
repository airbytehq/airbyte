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
from typing import Any, Iterator, Sequence

import backoff
import pendulum as pendulum
from base_python.entrypoint import logger  # FIXME (Eugene K): register logger as standard python logger
from facebook_business.exceptions import FacebookRequestError

from .common import retry_pattern

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)


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
    def entity_prefix(self):
        """Prefix of fields in filter"""

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

    def _state_filter(self):
        """Additional filters associated with state if any set"""
        if self._state:
            return {
                "filtering": [
                    {
                        "field": f"{self.entity_prefix}.{self.state_pk}",
                        "operator": "GREATER_THAN",
                        "value": self._state.int_timestamp,
                    },
                ],
            }

        return {}

    def state_filter(self, records: Iterator[dict]) -> Iterator[Any]:
        """Apply state filter to set of records, update cursor(state) if necessary in the end"""
        latest_cursor = None
        for record in records:
            cursor = pendulum.parse(record[self.state_pk])
            if self._state and self._state >= cursor:
                continue
            latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor
            yield record

        if latest_cursor:
            stream_name = self.__class__.__name__
            if stream_name.endswith("API"):
                stream_name = stream_name[:-3]
            logger.info(f"Advancing bookmark for {stream_name} stream from {self._state} to {latest_cursor}")
            self._state = max(latest_cursor, self._state) if self._state else latest_cursor


class AdCreativeAPI(StreamAPI):
    """AdCreative is not an iterable stream as it uses the batch endpoint
    doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup/adcreatives/
    """

    BATCH_SIZE = 50

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        ad_creative = self._get_creatives()

        # Create the initial batch
        api_batch = self._api._api.new_batch()
        records = []

        def success(response):
            records.append(response.json())

        def failure(response):
            raise response.error()

        # This loop syncs minimal AdCreative objects
        for i, creative in enumerate(ad_creative, start=1):
            # Execute and create a new batch for every BATCH_SIZE added
            if i % self.BATCH_SIZE == 0:
                api_batch.execute()
                api_batch = self._api._api.new_batch()
                yield from records
                records[:] = []

            # Add a call to the batch with the full object
            creative.api_get(fields=fields, batch=api_batch, success=success, failure=failure)

        # Ensure the final batch is executed
        api_batch.execute()
        yield from records

    @backoff_policy
    def _get_creatives(self):
        return self._api.account.get_ad_creatives(params={"limit": self.result_return_limit})


class AdsAPI(IncrementalStreamAPI):
    """ doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup """

    entity_prefix = "ad"
    state_pk = "updated_time"

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        ads = self._get_ads({"limit": self.result_return_limit})
        for record in self.state_filter(ads):
            yield self._extend_record(record, fields=fields)

    @backoff_policy
    def _get_ads(self, params):
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        return self._api.account.get_ads(params={**params, **self._state_filter()}, fields=[self.state_pk])

    @backoff_policy
    def _extend_record(self, ad, fields):
        return ad.api_get(fields=fields).export_all_data()


class AdSetsAPI(IncrementalStreamAPI):
    """ doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign """

    entity_prefix = "adset"
    state_pk = "updated_time"

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        adsets = self._get_ad_sets({"limit": self.result_return_limit})

        for adset in self.state_filter(adsets):
            yield self._extend_record(adset, fields=fields)

    @backoff_policy
    def _get_ad_sets(self, params):
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        return self._api.account.get_ad_sets(params={**params, **self._state_filter()}, fields=[self.state_pk])

    @backoff_policy
    def _extend_record(self, ad_set, fields):
        return ad_set.api_get(fields=fields).export_all_data()


class CampaignAPI(IncrementalStreamAPI):
    entity_prefix = "campaign"
    state_pk = "updated_time"

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Read available campaigns"""
        pull_ads = "ads" in fields
        fields = [k for k in fields if k != "ads"]
        campaigns = self._get_campaigns({"limit": self.result_return_limit})
        for campaign in self.state_filter(campaigns):
            yield self._extend_record(campaign, fields=fields, pull_ads=pull_ads)

    @backoff_policy
    def _extend_record(self, campaign, fields, pull_ads):
        """Request additional attributes for campaign"""
        campaign_out = campaign.api_get(fields=fields).export_all_data()
        if pull_ads:
            campaign_out["ads"] = {"data": []}
            ids = [ad["id"] for ad in campaign.get_ads()]
            for ad_id in ids:
                campaign_out["ads"]["data"].append({"id": ad_id})
        return campaign_out

    @backoff_policy
    def _get_campaigns(self, params):
        """Separate method to request list of campaigns
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        return self._api.account.get_campaigns(params={**params, **self._state_filter()}, fields=[self.state_pk])


#
# FIXME: Disabled until we populate test account with AdsInsights data to test
#  https://github.com/airbytehq/airbyte/issues/1709
#
# class AdsInsightAPI(IncrementalStreamAPI):
#     entity_prefix = ""
#     state_pk = "date_start"
#
#     ALL_ACTION_ATTRIBUTION_WINDOWS = [
#         "1d_click",
#         "7d_click",
#         "28d_click",
#         "1d_view",
#         "7d_view",
#         "28d_view",
#     ]
#
#     ALL_ACTION_BREAKDOWNS = [
#         "action_type",
#         "action_target_id",
#         "action_destination",
#     ]
#
#     # Some automatic fields (primary-keys) cannot be used as 'fields' query params.
#     INVALID_INSIGHT_FIELDS = [
#         "impression_device",
#         "publisher_platform",
#         "platform_position",
#         "age",
#         "gender",
#         "country",
#         "placement",
#         "region",
#         "dma",
#     ]
#
#     MAX_WAIT_TO_START_SECONDS = 2 * 60
#     MAX_WAIT_TO_FINISH_SECONDS = 30 * 60
#     MAX_ASYNC_SLEEP_SECONDS = 5 * 60
#
#     action_breakdowns = ALL_ACTION_BREAKDOWNS
#     level = "ad"
#     action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
#     time_increment = 1
#     buffer_days = 28
#
#     def __init__(self, api, start_date, breakdowns=None):
#         super().__init__(api=api)
#         self.start_date = start_date
#         self._state = start_date
#         self.breakdowns = breakdowns
#
#     def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
#         for params in self._params(fields=fields):
#             for rec in self.state_filter(obj.export_all_data() for obj in self._get_insights(params)):
#                 yield rec
#
#     def _params(self, fields: Sequence[str] = None) -> Iterator[dict]:
#         buffered_start_date = self._state.subtract(days=self.buffer_days)
#         end_date = pendulum.now()
#
#         fields = list(set(fields) - set(self.INVALID_INSIGHT_FIELDS))
#
#         while buffered_start_date <= end_date:
#             yield {
#                 "level": self.level,
#                 "action_breakdowns": self.action_breakdowns,
#                 "breakdowns": self.breakdowns,
#                 "limit": self.result_return_limit,
#                 "fields": fields,
#                 "time_increment": self.time_increment,
#                 "action_attribution_windows": self.action_attribution_windows,
#                 "time_ranges": [{"since": buffered_start_date.to_date_string(), "until": buffered_start_date.to_date_string()}],
#             }
#             buffered_start_date = buffered_start_date.add(days=1)
#
#     @backoff_policy
#     def _get_insights(self, params):
#         return self._api.account.get_insights(params=params)
