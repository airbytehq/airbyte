#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from copy import deepcopy

from pytest import fixture


@fixture
def config():
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh",
        "region": "NA",
        "look_back_window": 3,
        "report_record_types": []
    }


@fixture
def config_gen(config):
    def inner(**kwargs):
        new_config = deepcopy(config)
        # WARNING, no support deep dictionaries
        new_config.update(kwargs)
        return {k: v for k, v in new_config.items() if v is not ...}

    return inner


@fixture
def profiles_response():
    return """
[{"profileId":3991703629696934,"countryCode":"CA","currencyCode":"CAD","dailyBudget":9.99999999E8,"timezone":"America/Los_Angeles","accountInfo":{"marketplaceStringId":"A2EUQ1WTGCTBG2","id":"A3LUQZ2NBMFGO4","type":"seller","name":"The Airbyte Store","validPaymentMethod":true}},{"profileId":2935840597082037,"countryCode":"CA","currencyCode":"CAD","timezone":"America/Los_Angeles","accountInfo":{"marketplaceStringId":"A2EUQ1WTGCTBG2","id":"ENTITY1T4PQ8E0Y1LVJ","type":"vendor","name":"test","validPaymentMethod":false}},{"profileId":3664951271230581,"countryCode":"MX","currencyCode":"MXN","dailyBudget":9.99999999E8,"timezone":"America/Los_Angeles","accountInfo":{"marketplaceStringId":"A1AM78C64UM0Y8","id":"A3LUQZ2NBMFGO4","type":"seller","name":"The Airbyte Store","validPaymentMethod":true}},{"profileId":3312910465837761,"countryCode":"US","currencyCode":"USD","dailyBudget":9.99999999E8,"timezone":"America/Los_Angeles","accountInfo":{"marketplaceStringId":"ATVPDKIKX0DER","id":"A3LUQZ2NBMFGO4","type":"seller","name":"The Airbyte Store","validPaymentMethod":true}}]
"""


@fixture
def portfolios_response():
    return """
[{"portfolioId":253945852845204,"name":"Test Portfolio 2","inBudget":true,"state":"enabled","creationDate":1687510907465,"lastUpdatedDate":1687510907465,"servingStatus":"PORTFOLIO_STATUS_ENABLED"},{"portfolioId":270076898441727,"name":"Test Portfolio","budget":{"amount":1.0,"currencyCode":"USD","policy":"dateRange","startDate":"20230623","endDate":"20230624"},"inBudget":true,"state":"enabled","creationDate":1687510616329,"lastUpdatedDate":1687514774484,"servingStatus":"PORTFOLIO_STATUS_ENABLED"}]
"""


@fixture
def campaigns_response():
    return """
[{"campaignId":37387403419888,"name":"sswdd","tactic":"T00020","startDate":"20220101","state":"enabled","costType":"cpc","budget":3.0,"budgetType":"daily","deliveryProfile":"as_soon_as_possible"},{"campaignId":59249214322256,"name":"My test camp","tactic":"T00020","startDate":"20220101","state":"enabled","costType":"cpc","budget":3.0,"budgetType":"daily","deliveryProfile":"as_soon_as_possible"},{"campaignId":16117299922278,"name":"ssw","tactic":"T00020","startDate":"20220101","state":"enabled","costType":"cpc","budget":3.0,"budgetType":"daily","deliveryProfile":"as_soon_as_possible"},{"campaignId":202914386115504,"name":"ssdf","tactic":"T00020","startDate":"20220101","state":"enabled","costType":"cpc","budget":3.0,"budgetType":"daily","deliveryProfile":"as_soon_as_possible"}]
"""


@fixture
def adgroups_response():
    return """
[{"name":"string","campaignId":0,"defaultBid":0,"bidOptimization":"clicks","state":"enabled","adGroupId":0,"tactic":"T00020"}]
"""


@fixture
def product_ads_response():
    return """
[{"state":"enabled","adId":0,"adGroupId":0,"campaignId":0,"asin":"string","sku":"string"}]
"""


@fixture
def targeting_response():
    return """
[{"targetId":123,"adGroupId":321,"state":"enabled","expressionType":"manual","bid":1.5,"expression":[{"type":"asinSameAs","value":"B0123456789"}],"resolvedExpression":[{"type":"views","values":{"type":"asinCategorySameAs","value":"B0123456789"}}]}]
"""


@fixture
def attribution_report_response():
    def _internal(report_type: str):
        responses = {
            "PRODUCTS": {
                "reports": [
                    {
                        "date": "20220829",
                        "attributedDetailPageViewsClicks14d": "0",
                        "attributedPurchases14d": "0",
                        "adGroupId": "bestselling_fan-dusters",
                        "advertiserName": "name",
                        "productName": "some product name",
                        "productCategory": "Chemicals",
                        "productSubcategory": "Applicators",
                        "brandHaloAttributedPurchases14d": "0",
                        "brandHaloUnitsSold14d": "0",
                        "attributedNewToBrandSales14d": "0",
                        "attributedAddToCartClicks14d": "0",
                        "brandHaloNewToBrandPurchases14d": "0",
                        "brandName": "name",
                        "marketplace": "AMAZON.COM",
                        "brandHaloAttributedSales14d": "0",
                        "campaignId": "my-campaign",
                        "brandHaloNewToBrandUnitsSold14d": "0",
                        "productAsin": "AAAAAAA",
                        "productConversionType": "Brand Halo",
                        "attributedNewToBrandUnitsSold14d": "0",
                        "brandHaloAttributedAddToCartClicks14d": "0",
                        "attributedNewToBrandPurchases14d": "0",
                        "unitsSold14d": "0",
                        "productGroup": "Automotive",
                        "brandHaloNewToBrandSales14d": "0",
                        "publisher": "Display - Other",
                        "brandHaloDetailPageViewsClicks14d": "0",
                        "attributedSales14d": "0",
                    }
                ]
            },
            "PERFORMANCE_ADGROUP": {
                "reports": [
                    {
                        "date": "20220829",
                        "attributedAddToCartClicks14d": "5",
                        "brb_bonus_amount": "14.280000000000001",
                        "campaignId": "16719043411",
                        "attributedDetailPageViewsClicks14d": "30",
                        "attributedPurchases14d": "3",
                        "attributedTotalAddToCartClicks14d": "5",
                        "attributedTotalPurchases14d": "3",
                        "adGroupId": "135021988277",
                        "advertiserName": "Eversprout",
                        "totalUnitsSold14d": "4",
                        "unitsSold14d": "4",
                        "Click-throughs": "30",
                        "publisher": "Google Ads",
                        "attributedTotalDetailPageViewsClicks14d": "30",
                        "attributedSales14d": "191.95999999999998",
                        "totalAttributedSales14d": "191.95999999999998",
                    }
                ]
            },
            "PERFORMANCE_CAMPAIGN": {
                "reports": [
                    {
                        "date": "20220830",
                        "attributedAddToCartClicks14d": "1",
                        "brb_bonus_amount": "0",
                        "campaignId": "3936789099315437-B082P9Y919",
                        "attributedDetailPageViewsClicks14d": "9",
                        "attributedPurchases14d": "0",
                        "attributedTotalAddToCartClicks14d": "1",
                        "attributedTotalPurchases14d": "0",
                        "advertiserName": "Eversprout",
                        "totalUnitsSold14d": "0",
                        "unitsSold14d": "0",
                        "Click-throughs": "12",
                        "attributedTotalDetailPageViewsClicks14d": "16",
                        "attributedSales14d": "0",
                        "totalAttributedSales14d": "0",
                    }
                ]
            },
            "PERFORMANCE_CREATIVE": {
                "reports": [
                    {
                        "date": "20220830",
                        "attributedAddToCartClicks14d": "0",
                        "campaignId": "16719043411",
                        "attributedDetailPageViewsClicks14d": "0",
                        "attributedPurchases14d": "0",
                        "attributedTotalAddToCartClicks14d": "0",
                        "attributedTotalPurchases14d": "0",
                        "adGroupId": "135021988277",
                        "advertiserName": "Eversprout",
                        "creativeId": "135021988277",
                        "totalUnitsSold14d": "0",
                        "unitsSold14d": "0",
                        "Click-throughs": "1",
                        "publisher": "Google Ads",
                        "attributedTotalDetailPageViewsClicks14d": "0",
                        "attributedSales14d": "0",
                        "totalAttributedSales14d": "0",
                    }
                ]
            },
        }

        return json.dumps(responses[report_type])

    return _internal
