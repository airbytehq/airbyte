#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.streams import Stream
from source_amazon_seller_partner import SourceAmazonSellerPartner
from source_amazon_seller_partner.source import boto3


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
        "aws_access_key": "aws_access_key",
        "aws_secret_key": "aws_secret_key",
        "role_arn": "arn:aws:iam::123456789098:role/some-role",
        "aws_environment": "SANDBOX",
        "region": "US",
    }


@pytest.fixture
def sts_credentials():
    return {
        "Credentials": {
            "AccessKeyId": "foo",
            "SecretAccessKey": "bar",
            "SessionToken": "foobar",
        }
    }


@pytest.fixture
def mock_boto_client(mocker, sts_credentials):
    boto_client = MagicMock()
    mocker.patch.object(boto3, "client", return_value=boto_client)
    boto_client.assume_role.return_value = sts_credentials
    boto_client.get_session_token.return_value = sts_credentials
    return boto_client


def test_streams(connector_source, connector_config, mock_boto_client):
    for stream in connector_source.streams(connector_config):
        assert isinstance(stream, Stream)


@pytest.mark.parametrize("arn", ("arn:aws:iam::123456789098:user/some-user", "arn:aws:iam::123456789098:role/some-role"))
def test_stream_with_good_iam_arn_value(mock_boto_client, connector_source, connector_config, arn):
    connector_config["role_arn"] = arn
    result = connector_source.get_sts_credentials(connector_config)
    assert "Credentials" in result
    if "user" in arn:
        mock_boto_client.get_session_token.assert_called_once()
    if "role" in arn:
        mock_boto_client.assume_role.assert_called_once_with(RoleArn=arn, RoleSessionName="guid")


def test_stream_with_bad_iam_arn_value(connector_source, connector_config, mock_boto_client):
    connector_config["role_arn"] = "bad-arn"
    with pytest.raises(ValueError) as e:
        connector_source.get_sts_credentials(connector_config)
        assert "Invalid" in e.message
