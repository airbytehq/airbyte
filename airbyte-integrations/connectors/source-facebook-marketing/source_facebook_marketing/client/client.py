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

from datetime import datetime
from typing import Iterator, Sequence, Tuple

import backoff
from base_python import BaseClient
from base_python.entrypoint import logger  # FIXME (Eugene K): register logger as standard python logger
from cached_property import cached_property
from dateutil.parser import isoparse
from facebook_business import FacebookAdsApi
from facebook_business.adobjects import user as fb_user
from facebook_business.exceptions import FacebookRequestError

from .common import FacebookAPIException, retry_pattern


class StreamAPI:
    result_return_limit = 100

    def __init__(self, api):
        self._api = api

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        raise NotImplementedError


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

    @retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
    def _get_creatives(self):
        return self._api.account.get_ad_creatives(params={"limit": self.result_return_limit})


class AdsAPI(StreamAPI):
    """
    doc: https://developers.facebook.com/docs/marketing-api/reference/adgroup
    """

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        ads = self._get_ads({"limit": self.result_return_limit})
        for recordset in ads:
            for record in recordset:
                yield self._extend_record(record, fields=fields)

    @retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
    def _get_ads(self, params):
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        return self._api.account.get_ads(params=params)

    @retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
    def _extend_record(self, ad, fields):
        return ad.api_get(fields=fields).export_all_data()


class AdSetsAPI(StreamAPI):
    """ doc: https://developers.facebook.com/docs/marketing-api/reference/ad-campaign """

    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        adsets = self._get_ad_sets({"limit": self.result_return_limit})

        for adset in adsets:
            yield self._extend_record(adset, fields=fields)

    @retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
    def _get_ad_sets(self, params):
        """
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        return self._api.account.get_ad_sets(params=params)

    @retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
    def _extend_record(self, ad_set, fields):
        return ad_set.api_get(fields=fields).export_all_data()


class CampaignAPI(StreamAPI):
    def list(self, fields: Sequence[str] = None) -> Iterator[dict]:
        """Read available campaigns"""
        pull_ads = "ads" in fields
        fields = [k for k in fields if k != "ads"]
        campaigns = self._get_campaigns({"limit": self.result_return_limit})
        for campaign in campaigns:
            yield self._extend_record(campaign, fields=fields, pull_ads=pull_ads)

    @retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
    def _extend_record(self, campaign, fields, pull_ads):
        """Request additional attributes for campaign"""
        campaign_out = campaign.api_get(fields=fields).export_all_data()
        if pull_ads:
            campaign_out["ads"] = {"data": []}
            ids = [ad["id"] for ad in campaign.get_ads()]
            for ad_id in ids:
                campaign_out["ads"]["data"].append({"id": ad_id})
        return campaign_out

    @retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
    def _get_campaigns(self, params):
        """Separate method to request list of campaigns
        This is necessary because the functions that call this endpoint return
        a generator, whose calls need decorated with a backoff.
        """
        return self._api.account.get_campaigns(params=params)


class AdsInsightAPI(StreamAPI):
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
        end_date = datetime.now()

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

    @retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)
    def _get_insights(self, params):
        return self._api.account.get_insights(params=params)


class Client(BaseClient):
    def __init__(self, account_id: str, access_token: str, start_date: str):
        super().__init__()
        self._api = FacebookAdsApi.init(access_token=access_token)
        self._account_id = account_id
        self._start_date = isoparse(start_date)

    @cached_property
    def account(self):
        return self._find_account(self._account_id)

    def stream__campaigns(self, fields=None, **kwargs):
        yield from CampaignAPI(self).list(fields)

    def stream__adsets(self, fields=None, **kwargs):
        yield from AdSetsAPI(self).list(fields)

    def stream__ads(self, fields=None, **kwargs):
        yield from AdsAPI(self).list(fields)

    def stream__adcreatives(self, fields=None, **kwargs):
        yield from AdCreativeAPI(self).list(fields)

    def stream__ads_insights(self, fields=None, **kwargs):
        client = AdsInsightAPI(self, start_date=self._start_date, **kwargs)
        yield from client.list(fields)

    def stream__ads_insights_age_and_gender(self, fields=None, **kwargs):
        yield from self.stream__ads_insights(fields=fields, breakdowns=["age", "gender"])

    def stream__ads_insights_country(self, fields=None, **kwargs):
        yield from self.stream__ads_insights(fields=fields, breakdowns=["country"])

    def stream__ads_insights_platform_and_device(self, fields=None, **kwargs):
        yield from self.stream__ads_insights(fields=fields, breakdowns=["publisher_platform", "platform_position", "impression_device"])

    def stream__ads_insights_region(self, fields=None, **kwargs):
        yield from self.stream__ads_insights(fields=fields, breakdowns=["region"])

    def stream__ads_insights_dma(self, fields=None, **kwargs):
        yield from self.stream__ads_insights(fields=fields, breakdowns=["dma"])

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
