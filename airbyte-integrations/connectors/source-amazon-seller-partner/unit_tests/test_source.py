#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
from unittest.mock import patch

import freezegun
import pytest
from source_amazon_seller_partner import SourceAmazonSellerPartner
from source_amazon_seller_partner.components import AmazonSPOauthAuthenticator
from source_amazon_seller_partner.utils import AmazonConfigException

from airbyte_cdk.sources.streams import Stream


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
                "report_name": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
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
    assert SourceAmazonSellerPartner(
        config=connector_config_with_report_options,
        catalog=None,
        state=None,
    ).check_connection(logger, connector_config_with_report_options) == (True, None)


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
        json={"payload": {"Orders": [{"LastUpdateDate": "2024-06-02T00:00:00Z"}]}},
    )
    assert SourceAmazonSellerPartner(
        config=connector_config_with_report_options,
        catalog=None,
        state=None,
    ).check_connection(logger, connector_config_with_report_options) == (True, None)


@pytest.mark.parametrize(
    ("report_name", "stream_name_w_options"),
    (
        (
            "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
            [
                (
                    "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
                    [
                        {"option_name": "some_name_1", "option_value": "some_value_1"},
                        {"option_name": "some_name_2", "option_value": "some_value_2"},
                    ],
                ),
            ],
        ),
        ("SOME_OTHER_STREAM", []),
    ),
)
def test_get_stream_report_options_list(connector_config_with_report_options, report_name, stream_name_w_options):
    assert (
        list(
            SourceAmazonSellerPartner(
                config=connector_config_with_report_options,
                catalog=None,
                state=None,
            ).get_stream_report_kwargs(report_name, connector_config_with_report_options)
        )
        == stream_name_w_options
    )


def test_config_report_options_validation_error_duplicated_streams(connector_config_with_report_options):
    connector_config_with_report_options["report_options_list"].append(connector_config_with_report_options["report_options_list"][0])
    with pytest.raises(AmazonConfigException) as e:
        SourceAmazonSellerPartner(
            config=connector_config_with_report_options,
            catalog=None,
            state=None,
        ).validate_stream_report_options(connector_config_with_report_options)
    assert e.value.message == "Stream name should be unique among all Report options list"


def test_config_report_options_validation_error_duplicated_options(connector_config_with_report_options):
    connector_config_with_report_options["report_options_list"][0]["options_list"].append(
        connector_config_with_report_options["report_options_list"][0]["options_list"][0]
    )
    with pytest.raises(AmazonConfigException) as e:
        SourceAmazonSellerPartner(
            config=connector_config_with_report_options,
            catalog=None,
            state=None,
        ).validate_stream_report_options(connector_config_with_report_options)
    assert e.value.message == "Option names should be unique for `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` report options"


def test_streams(connector_config_without_start_date):
    for stream in SourceAmazonSellerPartner(
        config=connector_config_without_start_date,
        catalog=None,
        state=None,
    ).streams(connector_config_without_start_date):
        assert isinstance(stream, Stream)


def test_streams_count(connector_config_without_start_date, monkeypatch):
    streams = SourceAmazonSellerPartner(
        config=connector_config_without_start_date,
        catalog=None,
        state=None,
    ).streams(connector_config_without_start_date)
    assert len(streams) == 44


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
            SourceAmazonSellerPartner(
                config=config,
                catalog=None,
                state=None,
            ).validate_replication_dates(config)
        assert e.value.message == "End Date should be greater than or equal to Start Date"
    else:
        assert (
            SourceAmazonSellerPartner(
                config=config,
                catalog=None,
                state=None,
            ).validate_replication_dates(config)
            is None
        )
