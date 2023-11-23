#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.streams import Stream
from source_amazon_seller_partner import SourceAmazonSellerPartner
from source_amazon_seller_partner.utils import AmazonConfigException


@pytest.fixture
def connector_config_with_report_options():
    return {
        "replication_start_date": "2017-01-25T00:00:00Z",
        "replication_end_date": "2017-02-25T00:00:00Z",
        "refresh_token": "Atzr|IwEBIP-abc123",
        "app_id": "amzn1.sp.solution.2cfa6ca8-2c35-123-456-78910",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
        "report_options_list": [
            {
                "stream_name": "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA",
                "options_list": [
                    {
                        "option_name": "some_name_1",
                        "option_value": "some_value_1"
                    },

                    {
                        "option_name": "some_name_2",
                        "option_value": "some_value_2"
                    }
                ]
            }
        ],
    }


NOT_SUPPORTED_STREAMS_REPORT_OPTIONS = ["VendorDirectFulfillmentShipping", "Orders", "OrderItems", "ListFinancialEventGroups", "ListFinancialEvents"]


def test_config_report_options(connector_config_with_report_options):
    streams = SourceAmazonSellerPartner().streams(connector_config_with_report_options)
    fba_fulfilment_stream = [x for x in streams if x.name == "GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA"][0]
    assert fba_fulfilment_stream.report_options() == {"option_name": "some_name_2", "option_value": "some_value_2"}
    all_other_streams = (x for x in streams if
                         x.name not in ["GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA", *NOT_SUPPORTED_STREAMS_REPORT_OPTIONS])
    for streams in all_other_streams:
        assert not streams.report_options()


def test_config_report_options_validation_error_duplicated_streams(connector_config_with_report_options):
    connector_config_with_report_options["report_options_list"].append(connector_config_with_report_options["report_options_list"][0])
    with pytest.raises(AmazonConfigException) as e:
        SourceAmazonSellerPartner().validate_stream_report_options(connector_config_with_report_options)
    assert e.value.message == "Stream name should be unique among all Report options list"


def test_config_report_options_validation_error_duplicated_options(connector_config_with_report_options):
    connector_config_with_report_options["report_options_list"][0]['options_list'].append(connector_config_with_report_options["report_options_list"][0]['options_list'][0])
    with pytest.raises(AmazonConfigException) as e:
        SourceAmazonSellerPartner().validate_stream_report_options(connector_config_with_report_options)
    assert e.value.message == "Option names should be unique for `GET_FBA_FULFILLMENT_CUSTOMER_RETURNS_DATA` report options"


@pytest.fixture
def connector_config_without_start_date():
    return {
        "refresh_token": "Atzr|IwEBIP-abc123",
        "app_id": "amzn1.sp.solution.2cfa6ca8-2c35-123-456-78910",
        "lwa_app_id": "amzn1.application-oa2-client.abc123",
        "lwa_client_secret": "abc123",
        "aws_environment": "SANDBOX",
        "region": "US",
    }


def test_streams(connector_source, connector_config):
    for stream in connector_source.streams(connector_config):
        assert isinstance(stream, Stream)


def test_streams_connector_config_without_start_date(connector_source, connector_config_without_start_date):
    for stream in connector_source.streams(connector_config_without_start_date):
        assert isinstance(stream, Stream)
