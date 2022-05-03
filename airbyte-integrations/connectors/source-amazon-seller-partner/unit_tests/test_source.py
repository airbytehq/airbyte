import pytest
from source_amazon_seller_partner import SourceAmazonSellerPartner
from source_amazon_seller_partner import ConnectorConfig
from airbyte_cdk.models import ConnectorSpecification
from airbyte_cdk.sources.streams import Stream


@pytest.fixture
def connector_source():
    return SourceAmazonSellerPartner()


@pytest.fixture
def connector_config():
    return ConnectorConfig(
        replication_start_date="2017-01-25T00:00:00Z",
        refresh_token="Atzr|IwEBIP-abc123",
        lwa_app_id="amzn1.application-oa2-client.abc123",
        lwa_client_secret="abc123",
        aws_access_key="aws_access_key",
        aws_secret_key="aws_secret_key",
        role_arn="arn:aws:iam::123456789098:role/some-role",
        aws_environment="SANDBOX",
        region="US"
    )


class FakeBotoClient:
    role = {
        "Credentials": {
            "AccessKeyId": "foo",
            "SecretAccessKey": "bar",
            "SessionToken": "foobar",
        }
    }

    def assume_role(self, *args, **kwargs):
        return self.role

    def get_session_token(self, *args, **kwargs):
        return self.role


@pytest.fixture
def mock_boto_client(mocker):
    mocker.patch("boto3.client", return_value=FakeBotoClient())


def test_spec(connector_source):
    assert isinstance(connector_source.spec(), ConnectorSpecification)


def test_streams(connector_source, connector_config, mock_boto_client):
    for stream in connector_source.streams(connector_config):
        assert isinstance(stream, Stream)


def test_stream_user_role(connector_source, connector_config, mock_boto_client):
    connector_config.role_arn = "arn:aws:iam::123456789098:user/some-user"
    result = connector_source.get_sts_credentials(connector_config)
    assert "Credentials" in result


def test_stream_bad_arn_value(connector_source, connector_config, mock_boto_client):
    connector_config.role_arn = "bad-arn"
    with pytest.raises(ValueError) as e:
        connector_source.get_sts_credentials(connector_config)
        assert "Invalid" in e.message
