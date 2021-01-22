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

import os

from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adcreativelinkdata import AdCreativeLinkData
from facebook_business.adobjects.adcreativeobjectstoryspec import AdCreativeObjectStorySpec
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.campaign import Campaign

from client import Client
from facebook_business.adobjects.targeting import Targeting


class FakeDataFactory:
    @staticmethod
    def campaign(account: AdAccount, seed: int):
        params = {
            Campaign.Field.name: f"Fake Campaign {seed}",
            Campaign.Field.configured_status: Campaign.Status.paused,
            Campaign.Field.special_ad_categories: [],
            Campaign.Field.objective: Campaign.Objective.messages,
        }
        record = account.create_campaign(params=params)
        print(f"Campaign {record} created")
        return record

    @staticmethod
    def ad(account: AdAccount, adset: dict, creative: AdCreative, seed: int):
        # creatives = account.get_ad_creatives()
        params = {
            Ad.Field.name: f"Fake advertisement {seed}",
            Ad.Field.adset: adset,
            Ad.Field.creative: creative,
            Ad.Field.status: Ad.Status.paused,
        }
        record = account.create_ad(params=params)
        print(f"Advertisment {record} created")
        return record

    @staticmethod
    def adset(account: AdAccount, campaign: dict, seed: int):
        params = {
            AdSet.Field.name: f"Fake AdSet {seed}",
            AdSet.Field.campaign_id: campaign[Campaign.Field.id],
            AdSet.Field.daily_budget: 1000,
            AdSet.Field.billing_event: AdSet.BillingEvent.impressions,
            # AdSet.Field.optimization_goal: AdSet.OptimizationGoal.,
            AdSet.Field.bid_amount: 2,
            AdSet.Field.targeting: {
                Targeting.Field.geo_locations: {
                    "countries": ["US"],
                },
            },
        }
        record = account.create_ad_set(params=params)
        print(f"AdSet {record} created")
        return record

    @staticmethod
    def creative(account: AdAccount, seed: int):
        link_data = AdCreativeLinkData()
        link_data[AdCreativeLinkData.Field.message] = "My message"
        link_data[AdCreativeLinkData.Field.link] = "http://airbyte.io/"
        link_data[AdCreativeLinkData.Field.caption] = "www.domain.com"

        call_to_action = {
            "type": "SIGN_UP",
            "value": {
                "link": "http://airbyte.io/",
            },
        }

        link_data[AdCreativeLinkData.Field.call_to_action] = call_to_action

        object_story_spec = AdCreativeObjectStorySpec()
        object_story_spec[AdCreativeObjectStorySpec.Field.page_id] = 112704783733939
        object_story_spec[AdCreativeObjectStorySpec.Field.link_data] = link_data

        params = {
            AdCreative.Field.name: f"Fake AdCreative {seed}",
            AdCreative.Field.object_story_spec: object_story_spec,
        }
        record = account.create_ad_creative(params=params)
        print(f"AdCreative {record} created")
        return record


def main():
    client = Client(
        account_id=os.getenv("FB_ACCOUNT_ID", "212551616838260"),
        access_token=os.getenv(
            "FB_ACCESS_TOKEN",
            "EAAIiMrySdgkBANf507FCKOAy874goyqT7mAPTlEdfcRP24DNk4m4wlB7beZC9b8ccsNKV8nxlUtDRxa0KG0tJdkV3PRdLrssTVwccsmamvN1UORBG1UZADEcKSspK4deXbuo70N53uVpsSA8t2K6ZAlzKRGBhGZCXiLWiKPK3AZDZD",
        ),
        start_date="2020-04-21T18:53:15-0700",
    )
    print(client.account.get_promote_pages())
    for i in range(10):
        campaign = FakeDataFactory.campaign(account=client.account, seed=i)
        # creative = FakeDataFactory.creative(account=client.account, seed=i)
        creative = client.account.get_ad_creatives()[0]
        print(creative)
        for k in range(3):
            adset = FakeDataFactory.adset(account=client.account, campaign=campaign, seed=i * 100 + k)
            for h in range(3):
                FakeDataFactory.ad(account=client.account, creative=creative, adset=adset, seed=i * 100 + k)


if __name__ == "__main__":
    main()
