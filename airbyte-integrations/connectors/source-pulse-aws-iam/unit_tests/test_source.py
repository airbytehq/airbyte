import pytest
from source_pulse_aws_iam.source import SourcePulseAwsIam


@pytest.fixture
def role_arn_config():
    return {
        "provider": {
            "role_arn": "arn:aws:iam::123456789012:role/AirbyteRole",
            "external_id": "external-id-123",
            "region": "us-east-1"
        }
    }


@pytest.fixture
def access_key_config():
    return {
        "provider": {
            "aws_access_key_id": "FAKE_ACCESS_KEY",
            "aws_secret_access_key": "FAKE_SECRET_KEY",
            "region": "us-east-1"
        }
    }


def test_check_connection_access_key(mocker, access_key_config):
    mock_client = mocker.patch("boto3.client")
    source = SourcePulseAwsIam()
    success, error = source.check_connection(logger=None, config=access_key_config)
    assert success is True
    assert error is None


def test_check_connection_role_arn(mocker, role_arn_config):
    mock_sts_client = mocker.patch("boto3.client")
    mock_sts_client().assume_role.return_value = {
        "Credentials": {
            "AccessKeyId": "FAKE_TEMP_KEY",
            "SecretAccessKey": "FAKE_TEMP_SECRET",
            "SessionToken": "FAKE_SESSION_TOKEN"
        }
    }
    source = SourcePulseAwsIam()
    success, error = source.check_connection(logger=None, config=role_arn_config)
    assert success is True
    assert error is None
