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

import responses
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConnectorSpecification, Status, Type
from jsonschema import Draft4Validator
from source_amazon_ads import SourceAmazonAds


def setup_responses():
    responses.add(
        responses.POST,
        "https://api.amazon.com/auth/o2/token",
        json={"access_token": "alala", "expires_in": 10},
    )
    responses.add(
        responses.GET,
        "https://advertising-api.amazon.com/v2/profiles",
        json=[],
    )


@responses.activate
def test_discover(test_config):
    setup_responses()
    source = SourceAmazonAds()
    catalog = source.discover(None, test_config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]
    for schema in schemas:
        Draft4Validator.check_schema(schema)


def test_spec(test_config):
    source = SourceAmazonAds()
    spec = source.spec()
    assert isinstance(spec, ConnectorSpecification)


@responses.activate
def test_check(test_config):
    setup_responses()
    source = SourceAmazonAds()
    assert source.check(None, test_config) == AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert len(responses.calls) == 2


@responses.activate
def test_source_streams(test_config):
    setup_responses()
    source = SourceAmazonAds()
    streams = source.streams(test_config)
    assert len(streams) == 17
    actual_stream_names = {stream.name for stream in streams}
    expected_stream_names = set(
        [
            "profiles",
            "sponsored_display_campaigns",
            "sponsored_product_campaigns",
            "sponsored_product_ad_groups",
            "sponsored_product_keywords",
            "sponsored_product_negative_keywords",
            "sponsored_product_ads",
            "sponsored_product_targetings",
            "sponsored_products_report_stream",
            "sponsored_brands_campaigns",
            "sponsored_brands_ad_groups",
            "sponsored_brands_keywords",
            "sponsored_brands_report_stream",
        ]
    )
    assert not expected_stream_names - actual_stream_names
