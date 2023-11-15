#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from airbyte_cdk.sources.streams import Stream
from source_amazon_seller_partner import SourceAmazonSellerPartner


@pytest.fixture
def connector_source():
    return SourceAmazonSellerPartner()


@pytest.fixture
def connector_config():
    return {
        "replication_start_date": "2017-01-25T00:00:00Z",
        "replication_end_date": "2017-02-25T00:00:00Z",
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
