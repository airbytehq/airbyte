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

from pytest import fixture


@fixture
def test_config():
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "scope": "test_scope",
        "refresh_token": "test_refresh",
    }


@fixture
def profiles_response():
    return """
[{"profileId":3991703629696934,"countryCode":"CA","currencyCode":"CAD","dailyBudget":9.99999999E8,"timezone":"America/Los_Angeles","accountInfo":{"marketplaceStringId":"A2EUQ1WTGCTBG2","id":"A3LUQZ2NBMFGO4","type":"seller","name":"The Airbyte Store","validPaymentMethod":true}},{"profileId":2935840597082037,"countryCode":"CA","currencyCode":"CAD","timezone":"America/Los_Angeles","accountInfo":{"marketplaceStringId":"A2EUQ1WTGCTBG2","id":"ENTITY1T4PQ8E0Y1LVJ","type":"vendor","name":"test","validPaymentMethod":false}},{"profileId":3664951271230581,"countryCode":"MX","currencyCode":"MXN","dailyBudget":9.99999999E8,"timezone":"America/Los_Angeles","accountInfo":{"marketplaceStringId":"A1AM78C64UM0Y8","id":"A3LUQZ2NBMFGO4","type":"seller","name":"The Airbyte Store","validPaymentMethod":true}},{"profileId":3312910465837761,"countryCode":"US","currencyCode":"USD","dailyBudget":9.99999999E8,"timezone":"America/Los_Angeles","accountInfo":{"marketplaceStringId":"ATVPDKIKX0DER","id":"A3LUQZ2NBMFGO4","type":"seller","name":"The Airbyte Store","validPaymentMethod":true}}]
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
[{"targetId":123,"adGroupId":321,"state":"enabled","expressionType":"manual","bid":1.5,"expression":{"type":"asinSameAs","value":"B0123456789"},"resolvedExpression":{"type":"views","values":{"type":"asinCategorySameAs","value":"B0123456789"}}}]
"""
