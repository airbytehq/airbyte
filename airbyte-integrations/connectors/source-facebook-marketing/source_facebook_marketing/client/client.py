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
from typing import Iterator, Sequence, Tuple, Any, Mapping

import backoff
import pendulum as pendulum
from base_python import BaseClient
from base_python.entrypoint import logger  # FIXME (Eugene K): register logger as standard python logger
from cached_property import cached_property
from facebook_business import FacebookAdsApi
from facebook_business.adobjects import user as fb_user
from facebook_business.exceptions import FacebookRequestError

from .common import FacebookAPIException, retry_pattern

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
    def state_pk(self):
        """Name of the field associated with the state"""

    @property
    def state(self):
        return {self.state_pk: str(self._state)}

    @state.setter
    def state(self, value):
        self._state = self._cursor_from_record(value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state = None

    def _cursor_from_record(self, record: dict):
        short_name = self.state_pk.split('.')[-1]
        return pendulum.parse(record[short_name])

    def _state_filter(self):
        """Additional filters associated with state if any set"""
        if self.state:
            return {
                'filtering': [
                    {
                        'field': self.state_pk,
                        'operator': 'GREATER_THAN',
                        'value': self._state.int_timestamp,
                    },
                ],
            }

        return {}

    def state_filter(self, records: Iterator[dict]) -> Iterator[Any]:
        """ Apply state filter to set of records, update cursor(state) if necessary in the end
        """
        latest_cursor = None
        for record in records:
            cursor = pendulum.parse(record[self.state_pk])
            if self._state and self._state >= cursor:
                continue
            latest_cursor = max(cursor, latest_cursor) if latest_cursor else cursor
            yield record

        if latest_cursor:
            logger.info(f"Advancing bookmark for stream from {self._state} to {latest_cursor}")
            self._state = max(latest_cursor, self._state) if self._state else latest_cursor


class AdCreativeAPI(StreamAPI):
    """AdCreative is not an iterable stream as it uses the batch endpoint
    doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup/adcreatives/
    """

    BATCH_SIZE = 50

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        ad_creative = self._get_creatives()

        # Create the initial batch
        api_batch = self._api.new_batch()
        records = []

        def success(response):
            records.append(response)

        def failure(response):
            raise response.error()

        # This loop syncs minimal AdCreative objects
        for i, creative in enumerate(ad_creative):
            # Execute and create a new batch for every BATCH_SIZE added
            if i % self.BATCH_SIZE == 0:
                api_batch.execute()
                api_batch = self._api.new_batch()
                yield from records
                records[:] = []

            # Add a call to the batch with the full object
            creative.api_get(fields=fields, batch=api_batch, success=success, failure=failure)

        # Ensure the final batch is executed
        api_batch.execute()

    @backoff_policy
    def _get_creatives(self):
        return self._api.account.get_ad_creatives(params={"limit": self.result_return_limit})


class AdsAPI(IncrementalStreamAPI):
    """ doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup """
    state_pk = "ad.updated_time"

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
        return self._api.account.get_ads(params={**params, **self._state_filter()})

    @backoff_policy
    def _extend_record(self, ad, fields):
        return ad.api_get(fields=fields).export_all_data()


class AdSetsAPI(IncrementalStreamAPI):
    """ doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign """
    state_pk = "adset.updated_time"

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
        return self._api.account.get_ad_sets(params=params)

    @backoff_policy
    def _extend_record(self, ad_set, fields):
        return ad_set.api_get(fields=fields).export_all_data()


class CampaignAPI(IncrementalStreamAPI):
    state_pk = "campaign.updated_time"

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
        return self._api.account.get_campaigns(params=params)


class AdsInsightAPI(StreamAPI):
    state_pk = "date_start"

    ALL_ACTION_ATTRIBUTION_WINDOWS = [
        "1d_click",
        "7d_click",
        "28d_click",
        "1d_view",
        "7d_view",
        "28d_view",
    ]

    ALL_ACTION_BREAKDOWNS = [
        "action_type",
        "action_target_id",
        "action_destination",
    ]

    # Some automatic fields (primary-keys) cannot be used as 'fields' query params.
    INVALID_INSIGHT_FIELDS = [
        "impression_device",
        "publisher_platform",
        "platform_position",
        "age",
        "gender",
        "country",
        "placement",
        "region",
        "dma",
    ]

    action_breakdowns = ALL_ACTION_BREAKDOWNS
    level = "ad"
    action_attribution_windows = ALL_ACTION_ATTRIBUTION_WINDOWS
    time_increment = 1
    buffer_days = 28

    def __init__(self, api, start_date, breakdowns=None):
        super().__init__(api=api)
        self.start_date = start_date
        self.breakdowns = breakdowns

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        for params in self._params():
            for obj in self._get_insights(params):
                rec = obj.export_all_data()
                yield rec

    def _params(self, fields: Sequence[str] = None) -> Iterator[dict]:
        buffered_start_date = self.start_date.subtract(days=self.buffer_days)
        end_date = pendulum.now()

        fields = list(set(fields) - set(self.INVALID_INSIGHT_FIELDS))

        while buffered_start_date <= end_date:
            yield {
                "level": self.level,
                "action_breakdowns": self.action_breakdowns,
                "breakdowns": self.breakdowns,
                "limit": self.result_return_limit,
                "fields": fields,
                "time_increment": self.time_increment,
                "action_attribution_windows": self.action_attribution_windows,
                "time_ranges": [{"since": buffered_start_date.to_date_string(), "until": buffered_start_date.to_date_string()}],
            }
            buffered_start_date = buffered_start_date.add(days=1)

    @backoff_policy
    def _get_insights(self, params):
        return self._api.account.get_insights(params=params)


class Client(BaseClient):
    def __init__(self, account_id: str, access_token: str, start_date: str, include_deleted: bool = False):
        self._account_id = account_id
        self._start_date = pendulum.parse(start_date)
        self._include_deleted = include_deleted

        self._api = FacebookAdsApi.init(access_token=access_token)
        self._apis = {
            "campaigns": CampaignAPI(self),
            "adsets": AdSetsAPI(self),
            "ads": AdsAPI(self),
            "adcreatives": AdCreativeAPI(self),
            "ads_insights": AdsInsightAPI(self, start_date=self._start_date),
            "ads_insights_age_and_gender": AdsInsightAPI(self, start_date=self._start_date, breakdowns=["age", "gender"]),
            "ads_insights_country": AdsInsightAPI(self, start_date=self._start_date, breakdowns=["country"]),
            "ads_insights_region": AdsInsightAPI(self, start_date=self._start_date, breakdowns=["region"]),
            "ads_insights_dma": AdsInsightAPI(self, start_date=self._start_date, breakdowns=["dma"]),
            "ads_insights_platform_and_device": AdsInsightAPI(self, start_date=self._start_date,
                                                              breakdowns=["publisher_platform", "platform_position",
                                                                          "impression_device"])
        }
        super().__init__()

    def _enumerate_methods(self) -> Mapping[str, callable]:
        """Detect available streams and return mapping"""
        return {
            name: api.list
            for name, api in self._apis.items()
        }

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return hasattr(self._apis[name], 'state')

    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        return self._apis[name].state

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        self._apis[name].state = state

    @cached_property
    def account(self):
        return self._find_account(self._account_id)

    @staticmethod
    def _find_account(account_id: str):
        try:
            accounts = fb_user.User(fbid="me").get_ad_accounts()
            for account in accounts:
                if account["account_id"] == account_id:
                    return account
        except FacebookRequestError as exc:
            raise FacebookAPIException(f"Error: {exc.api_error_code()}, {exc.api_error_message()}") from exc

        raise FacebookAPIException("Couldn't find account with id {}".format(account_id))

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_message = None
        try:
            self._find_account(self._account_id)
        except FacebookAPIException as exc:
            logger.error(str(exc))  # we might need some extra details, so log original exception here
            alive = False
            error_message = str(exc)

        return alive, error_message
