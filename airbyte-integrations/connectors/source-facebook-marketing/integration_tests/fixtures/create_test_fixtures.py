from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.campaign import Campaign
from facebook_business.api import FacebookAdsApi
from typing import List, Set
import json

REQUIRED_CONFIG_KEYS = ["access_token", "app_secret", "app_id", "ad_account_id"]


def get_missing_fields(expected_fields: Set[str], actual: Set[str]) -> List[str]:
    return [f for f in expected_fields if f not in actual]


def read_credentials(path: str):
    with open(path, 'r') as creds_json:
        creds = json.load(creds_json)
        missing_fields = get_missing_fields(REQUIRED_CONFIG_KEYS, set(creds.keys()))
        if len(missing_fields) > 0:
            raise Exception(f"Input config at {path} does not contain required config keys: {missing_fields}")
        else:
            return creds


def create_campaign(ad_account: AdAccount):
    fields = [
    ]
    params = {
        'name': 'My campaign',
        'objective': 'LINK_CLICKS',
        'status': 'ACTIVE',
        'special_ad_categories': [],
    }
    return ad_account.create_campaign(fields=fields, params=params)


def create_adset(ad_account: AdAccount, campaign_id):
    print("campaign ID " + campaign_id)
    params = {
        'name': 'My Adset',
        'lifetime_budget': '200000',
        'start_time': '2021-01-01T10:12:46-0800',
        'end_time': '2021-12-31T10:12:46-0800',
        'campaign_id': campaign_id,
        'bid_amount': '500',
        'billing_event': 'IMPRESSIONS',
        'optimization_goal': 'POST_ENGAGEMENT',
        'targeting': {
            'geo_locations': {
                'countries': ['US'], 'regions': [{'key': '4081'}],
                'cities': [{'key': '777934', 'radius': 10, 'distance_unit': 'mile'}]
            },
            'interests': [{'id': 6003139266461, 'name': 'Movies'}],
        },
        'status': 'ACTIVE',
    }

    return ad_account.create_ad_set(fields=[], params=params)


def create_adcreative(ad_account: AdAccount):
    # Uploaded a random image to FB, this is the ID
    image_hash = "00dda74887ba52c3c8044cfa731a9776"
    params = {
        'name': 'Sample Creative',
        'object_story_spec': {
            'page_id': '112704783733939',
            'link_data': {
                'image_hash': image_hash,
                'link': 'https://www.facebook.com/AirbyteHQ/',
                'message': 'try it out'}
        },
    }
    return ad_account.create_ad_creative(fields=[], params=params)


def create_ad(ad_account: AdAccount, adset_id, creative_id):
    params = {
        'name': 'My test Ad',
        'adset_id': adset_id,
        'creative': {'creative_id': creative_id},
        'status': 'PAUSED'
    }
    return ad_account.create_ad(fields=[], params=params)


def main():
    # Follows https://developers.facebook.com/docs/marketing-apis/get-started/

    creds = read_credentials("secrets/fixtures_config.json")
    app_id = creds["app_id"]
    access_token = creds["access_token"]
    ad_account_id = creds["ad_account_id"]

    FacebookAdsApi.init(app_id, access_token=access_token)

    ad_account = AdAccount(ad_account_id)

    # create_campaign(ad_account)
    campaigns: List[Campaign] = ad_account.get_campaigns()
    print(f"CAMPAIGNS: {campaigns}")
    campaign_id = campaigns[0].get_id()

    # create_adset(ad_account, campaign_id)
    adsets: List[AdSet] = ad_account.get_ad_sets(fields=['start_time'])
    # adsets[0].api_update(params={'start_time': '2021-01-01T10:12:46-0800'})
    print(f"ADSETS: {adsets}")
    adset_id = adsets[0].get_id()

    # create_adcreative(ad_account)
    adcreatives = ad_account.get_ad_creatives()
    adcreative_id = adcreatives[0].get_id()
    print(f"CREATIVES: {adcreatives}")

    # create_ad(ad_account, adset_id, adcreative_id)
    ads: List[Ad] = ad_account.get_ads()
    print(f"ADS: {ads}")


if __name__ == '__main__':
    main()

