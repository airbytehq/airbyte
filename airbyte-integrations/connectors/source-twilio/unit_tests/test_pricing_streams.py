#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import json

import pytest
from conftest import TEST_CONFIG, get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read
from airbyte_cdk.test.mock_http import HttpMocker, HttpRequest, HttpResponse


PRICING_BASE = "https://pricing.twilio.com"


@HttpMocker()
def test_voice_pricing_follows_parent_pages_and_requests_details(http_mocker: HttpMocker):
    list_url = f"{PRICING_BASE}/v2/Voice/Countries"
    next_page_url = f"{list_url}?PageSize=1000&Page=2&PageToken=TOKEN"
    http_mocker.get(
        HttpRequest(url=list_url, query_params={"PageSize": "1000"}),
        HttpResponse(
            body=json.dumps(
                {
                    "countries": [{"iso_country": "US"}],
                    "meta": {"next_page_url": next_page_url},
                }
            ),
            status_code=200,
        ),
    )
    http_mocker.get(
        HttpRequest(
            url=list_url,
            query_params={"PageSize": "1000", "Page": "2", "PageToken": "TOKEN"},
        ),
        HttpResponse(
            body=json.dumps(
                {
                    "countries": [{"iso_country": "GB"}],
                    "meta": {},
                }
            ),
            status_code=200,
        ),
    )
    for country in ("US", "GB"):
        http_mocker.get(
            HttpRequest(url=f"{list_url}/{country}"),
            HttpResponse(
                body=json.dumps(
                    {
                        "country": country,
                        "iso_country": country,
                        "url": f"{list_url}/{country}",
                        "price_unit": "USD",
                        "inbound_call_prices": [],
                        "outbound_prefix_prices": [],
                    }
                ),
                status_code=200,
            ),
        )

    catalog = CatalogBuilder().with_stream("voice_pricing_countries", SyncMode.full_refresh).build()
    output = read(get_source(TEST_CONFIG), TEST_CONFIG, catalog)

    assert [record.record.data["iso_country"] for record in output.records] == ["US", "GB"]


@HttpMocker()
def test_phone_number_pricing_filters_non_purchasable_countries(http_mocker: HttpMocker):
    list_url = f"{PRICING_BASE}/v1/PhoneNumbers/Countries"
    http_mocker.get(
        HttpRequest(url=list_url, query_params={"PageSize": "1000"}),
        HttpResponse(
            body=json.dumps(
                {
                    "countries": [{"iso_country": "AQ"}, {"iso_country": "US"}],
                    "meta": {},
                }
            ),
            status_code=200,
        ),
    )
    http_mocker.get(
        HttpRequest(url=f"{list_url}/AQ"),
        HttpResponse(
            body=json.dumps(
                {
                    "url": None,
                    "country": None,
                    "price_unit": None,
                    "phone_number_prices": None,
                    "iso_country": None,
                }
            ),
            status_code=200,
        ),
    )
    http_mocker.get(
        HttpRequest(url=f"{list_url}/US"),
        HttpResponse(
            body=json.dumps(
                {
                    "country": "United States",
                    "iso_country": "US",
                    "url": f"{list_url}/US",
                    "price_unit": "USD",
                    "phone_number_prices": [
                        {
                            "base_price": "1.00",
                            "current_price": "1.00",
                            "number_type": "local",
                        }
                    ],
                }
            ),
            status_code=200,
        ),
    )

    catalog = CatalogBuilder().with_stream("phone_number_pricing_countries", SyncMode.full_refresh).build()
    output = read(get_source(TEST_CONFIG), TEST_CONFIG, catalog)

    assert len(output.records) == 1
    assert output.records[0].record.data["iso_country"] == "US"


@pytest.mark.parametrize(
    "stream_name,list_path,detail",
    [
        pytest.param(
            "voice_pricing_countries",
            "/v2/Voice/Countries",
            {
                "country": "United States",
                "iso_country": "US",
                "url": f"{PRICING_BASE}/v2/Voice/Countries/US",
                "price_unit": "USD",
                "inbound_call_prices": [{"base_price": "0.01", "current_price": "0.02", "number_type": "local"}],
                "outbound_prefix_prices": [],
            },
            id="voice",
        ),
        pytest.param(
            "messaging_pricing_countries",
            "/v1/Messaging/Countries",
            {
                "country": "United States",
                "iso_country": "US",
                "url": f"{PRICING_BASE}/v1/Messaging/Countries/US",
                "price_unit": "USD",
                "inbound_sms_prices": [{"base_price": "0.01", "current_price": "0.02", "number_type": "shortcode"}],
                "outbound_sms_prices": [
                    {
                        "carrier": "Example",
                        "mcc": "310",
                        "mnc": "260",
                        "prices": [{"base_price": "0.01", "current_price": "0.02", "number_type": "sms"}],
                    }
                ],
            },
            id="messaging",
        ),
        pytest.param(
            "phone_number_pricing_countries",
            "/v1/PhoneNumbers/Countries",
            {
                "country": "United States",
                "iso_country": "US",
                "url": f"{PRICING_BASE}/v1/PhoneNumbers/Countries/US",
                "price_unit": "USD",
                "phone_number_prices": [{"base_price": "1.00", "current_price": "1.00", "number_type": "local"}],
            },
            id="phone_number",
        ),
    ],
)
@HttpMocker()
def test_pricing_streams_emit_expected_fields(http_mocker: HttpMocker, stream_name: str, list_path: str, detail: dict):
    list_url = f"{PRICING_BASE}{list_path}"
    http_mocker.get(
        HttpRequest(url=list_url, query_params={"PageSize": "1000"}),
        HttpResponse(body=json.dumps({"countries": [{"iso_country": "US"}], "meta": {}}), status_code=200),
    )
    http_mocker.get(
        HttpRequest(url=f"{list_url}/US"),
        HttpResponse(body=json.dumps(detail), status_code=200),
    )

    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.full_refresh).build()
    output = read(get_source(TEST_CONFIG), TEST_CONFIG, catalog)

    assert len(output.records) == 1
    assert output.records[0].record.data == detail
