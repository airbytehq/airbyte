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

import jsonschema
import responses
from airbyte_cdk.models import AirbyteMessage, Type
from source_braintree.source import SourceBraintree


def get_stream_by_name(streams: list, stream_name: str):
    for stream in streams:
        if stream.name == stream_name:
            return stream


def test_source_streams(test_config):
    s = SourceBraintree()
    streams = s.streams(test_config)
    assert len(streams) == 7
    assert {stream.name for stream in streams} == {
        "customer_stream",
        "discount_stream",
        "dispute_stream",
        "transaction_stream",
        "merchant_account_stream",
        "plan_stream",
        "subscription_stream",
    }
    customers = get_stream_by_name(streams, "customer_stream")
    assert customers.supports_incremental
    discount_stream = get_stream_by_name(streams, "discount_stream")
    assert not discount_stream.supports_incremental


def test_discover(test_config):
    source = SourceBraintree()
    catalog = source.discover(None, test_config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]
    for schema in schemas:
        jsonschema.Draft7Validator.check_schema(schema)


def test_spec(test_config):
    s = SourceBraintree()
    schema = s.spec(None).connectionSpecification
    jsonschema.Draft4Validator.check_schema(schema)
    jsonschema.validate(instance=test_config, schema=schema)


@responses.activate
def test_check(test_config):
    s = SourceBraintree()
    responses.add(
        responses.POST,
        "https://api.sandbox.braintreegateway.com:443/merchants/mech_id/customers/advanced_search_ids",
        body=open("unit_tests/data/customers_ids.txt").read(),
    )
    assert s.check_connection(None, test_config) == (True, "")
