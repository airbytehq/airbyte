#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from unittest.mock import patch

import pytest
from airbyte_cdk.sources.streams import Stream
from source_amazon_seller_partner import SourceAmazonSellerPartner
from source_amazon_seller_partner.streams import VendorOrders
from source_amazon_seller_partner.utils import AmazonConfigException

logger = logging.getLogger("airbyte")


@pytest.fixture
def connector_config_with_report_options():
    return {
        "replication_start_date": "2017-01-25T00:00:00Z",
        "replication_end_date": "2017-02-25T00:00:00Z",
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "account_type": "Seller",
        "region": "US",
        "report_options_list": [
            {
                "stream_name": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
                "options_list": [
                    {"option_name": "some_name_1", "option_value": "some_value_1"},
                    {"option_name": "some_name_2", "option_value": "some_value_2"},
                ],
            },
        ],
    }


@pytest.fixture
def connector_vendor_config_with_report_options():
    return {
        "replication_start_date": "2017-01-25T00:00:00Z",
        "replication_end_date": "2017-02-25T00:00:00Z",
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "account_type": "Vendor",
        "region": "US",
        "report_options_list": [
            {
                "stream_name": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
                "options_list": [
                    {"option_name": "some_name_1", "option_value": "some_value_1"},
                    {"option_name": "some_name_2", "option_value": "some_value_2"},
                ],
            },
        ],
    }


@pytest.fixture
def connector_config_without_start_date():
    return {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
    }


def test_check_connection_with_vendor_report(mocker, requests_mock, connector_vendor_config_with_report_options):
    mocker.patch("time.sleep", lambda x: None)
    requests_mock.register_uri(
        "POST",
        "https://api.amazon.com/auth/o2/token",
        status_code=200,
        json={"access_token": "access_token", "expires_in": "3600"},
    )

    with patch.object(VendorOrders, "read_records", return_value=iter([{"some_key": "some_value"}])):
        assert SourceAmazonSellerPartner().check_connection(logger, connector_vendor_config_with_report_options) == (True, None)


def test_check_connection_with_orders_stop_iteration(requests_mock, connector_config_with_report_options):
    requests_mock.register_uri(
        "POST",
        "https://api.amazon.com/auth/o2/token",
        status_code=200,
        json={"access_token": "access_token", "expires_in": "3600"},
    )
    requests_mock.register_uri(
        "GET",
        "https://sandbox.sellingpartnerapi-na.amazon.com/orders/v0/orders",
        status_code=201,
        json={"payload": {"Orders": []}},
    )
    assert SourceAmazonSellerPartner().check_connection(logger, connector_config_with_report_options) == (True, None)


def test_check_connection_with_orders(requests_mock, connector_config_with_report_options):
    requests_mock.register_uri(
        "POST",
        "https://api.amazon.com/auth/o2/token",
        status_code=200,
        json={"access_token": "access_token", "expires_in": "3600"},
    )
    requests_mock.register_uri(
        "GET",
        "https://sandbox.sellingpartnerapi-na.amazon.com/orders/v0/orders",
        status_code=200,
        json={"payload": {"Orders": [{"some_key": "some_value"}]}},
    )
    assert SourceAmazonSellerPartner().check_connection(logger, connector_config_with_report_options) == (True, None)


@pytest.mark.parametrize(
    ("report_name", "options_list"),
    (
        (
            "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
            [
                {"option_name": "some_name_1", "option_value": "some_value_1"},
                {"option_name": "some_name_2", "option_value": "some_value_2"},
            ],
        ),
        ("SOME_OTHER_STREAM", None),
    ),
)
def test_get_stream_report_options_list(connector_config_with_report_options, report_name, options_list):
    assert SourceAmazonSellerPartner().get_stream_report_options_list(report_name, connector_config_with_report_options) == options_list


def test_config_report_options_validation_error_duplicated_streams(connector_config_with_report_options):
    connector_config_with_report_options["report_options_list"].append(connector_config_with_report_options["report_options_list"][0])
    with pytest.raises(AmazonConfigException) as e:
        SourceAmazonSellerPartner().validate_stream_report_options(connector_config_with_report_options)
    assert e.value.message == "Stream name should be unique among all Report options list"


def test_config_report_options_validation_error_duplicated_options(connector_config_with_report_options):
    connector_config_with_report_options["report_options_list"][0]["options_list"].append(
        connector_config_with_report_options["report_options_list"][0]["options_list"][0]
    )
    with pytest.raises(AmazonConfigException) as e:
        SourceAmazonSellerPartner().validate_stream_report_options(connector_config_with_report_options)
    assert e.value.message == "Option names should be unique for `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` report options"


def test_streams(connector_config_without_start_date):
    for stream in SourceAmazonSellerPartner().streams(connector_config_without_start_date):
        assert isinstance(stream, Stream)


@pytest.mark.parametrize(("deployment_mode", "expected_streams_count"), (("cloud", 44), ("oss", 53)))
def test_streams_count(deployment_mode, expected_streams_count, connector_config_without_start_date, monkeypatch):
    monkeypatch.setenv("DEPLOYMENT_MODE", deployment_mode)
    streams = SourceAmazonSellerPartner().streams(connector_config_without_start_date)
    assert len(streams) == expected_streams_count


@pytest.mark.parametrize(
    ("config", "should_raise"),
    (
        ({"replication_start_date": "2022-09-01T00:00:00Z", "replication_end_date": "2022-08-01T00:00:00Z"}, True),
        ({"replication_start_date": "2022-09-01T00:00:00Z", "replication_end_date": "2022-10-01T00:00:00Z"}, False),
        ({"replication_end_date": "2022-10-01T00:00:00Z"}, False),
        ({"replication_start_date": "2022-09-01T00:00:00Z"}, False),
        ({}, False),
    ),
)
def test_replication_dates_validation(config, should_raise):
    if should_raise:
        with pytest.raises(AmazonConfigException) as e:
            SourceAmazonSellerPartner().validate_replication_dates(config)
        assert e.value.message == "End Date should be greater than or equal to Start Date"
    else:
        assert SourceAmazonSellerPartner().validate_replication_dates(config) is None


@pytest.mark.parametrize(("deployment_mode", "common_streams_count"), (("cloud", 0), ("oss", 8)))
def test_spec(deployment_mode, common_streams_count, monkeypatch):
    monkeypatch.setenv("DEPLOYMENT_MODE", deployment_mode)
    oss_only_streams = {
        "GET_BRAND_ANALYTICS_MARKET_BASKET_REPORT",
        "GET_BRAND_ANALYTICS_SEARCH_TERMS_REPORT",
        "GET_BRAND_ANALYTICS_REPEAT_PURCHASE_REPORT",
        "GET_SALES_AND_TRAFFIC_REPORT",
        "GET_VENDOR_SALES_REPORT",
        "GET_VENDOR_INVENTORY_REPORT",
        "GET_VENDOR_NET_PURE_PRODUCT_MARGIN_REPORT",
        "GET_VENDOR_TRAFFIC_REPORT",
    }
    streams_with_report_options = SourceAmazonSellerPartner().spec(
        logger
    ).connectionSpecification["properties"]["report_options_list"]["items"]["properties"]["stream_name"]["enum"]
    assert len(set(streams_with_report_options).intersection(oss_only_streams)) == common_streams_count
