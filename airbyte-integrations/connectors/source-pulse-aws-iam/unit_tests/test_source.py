import pytest
from source_pulse_aws_iam.source import SourcePulseAwsIam
from source_pulse_aws_iam.streams import BaseAwsClient


@pytest.fixture
def role_arn_config():
    return {
        "provider": {
            "auth_type": "role",
            "role_arn": "arn:aws:iam::123456789012:role/AirbyteRole",
            "external_id": "external-id-123",
            "region": "us-east-1"
        }
    }

@pytest.fixture
def access_key_config():
    return {
        "provider": {
            "auth_type": "credentials",
            "aws_access_key_id": "FAKE_ACCESS_KEY",
            "aws_secret_access_key": "FAKE_SECRET_KEY",
            "region": "us-east-1"
        }
    }

def test_check_connection_access_key(mocker, access_key_config):
    mock_iam_client = mocker.MagicMock()
    mock_iam_client.list_users.return_value = {
        "Users": [
            {
                "UserName": "test-user",
                "UserId": "AIDXXXXXXXXXXXXXXXXX"
            }
        ]
    }

    mock_session = mocker.MagicMock()
    mock_session.client.side_effect = lambda service, **kwargs: mock_iam_client

    mocker.patch('boto3.Session', return_value=mock_session)

    source = SourcePulseAwsIam()
    success, error = source.check_connection(logger=mocker.MagicMock(), config=access_key_config)

    if not success:
        print(f"Connection check failed with error: {error}")

    mock_iam_client.list_users.assert_called_with(MaxItems=100)

    assert success is True
    assert error is None

def test_check_connection_role_arn(mocker, role_arn_config):
    from datetime import datetime
    mock_sts_client = mocker.MagicMock()
    mock_sts_client.assume_role.return_value = {
        "Credentials": {
            "AccessKeyId": "FAKE_TEMP_KEY",
            "SecretAccessKey": "FAKE_TEMP_SECRET",
            "SessionToken": "FAKE_SESSION_TOKEN",
            "Expiration": datetime(2024, 12, 31, 23, 59, 59)  # datetime object instead of string
        }
    }

    mock_iam_client = mocker.MagicMock()
    mock_iam_client.list_users.return_value = {
        "Users": [
            {
                "UserName": "test-user",
                "UserId": "AIDXXXXXXXXXXXXXXXXX"
            }
        ]
    }

    def mock_client(service, **kwargs):
        if service == 'sts':
            return mock_sts_client
        elif service == 'iam':
            return mock_iam_client
        return mocker.MagicMock()

    mocker.patch('boto3.client', side_effect=mock_client)

    mock_session = mocker.MagicMock()
    mock_session.client.side_effect = mock_client
    mocker.patch('boto3.Session', return_value=mock_session)

    mock_botocore_session = mocker.MagicMock()
    mocker.patch('botocore.session.get_session', return_value=mock_botocore_session)

    source = SourcePulseAwsIam()
    success, error = source.check_connection(logger=mocker.MagicMock(), config=role_arn_config)

    if not success:
        print(f"Connection check failed with error: {error}")

    mock_sts_client.assume_role.assert_called_with(
        RoleArn="arn:aws:iam::123456789012:role/AirbyteRole",
        ExternalId="external-id-123",
        RoleSessionName="airbyte-iam-session"
    )

    mock_iam_client.list_users.assert_called_with(MaxItems=100)

    assert success is True
    assert error is None

def test_check_connection_invalid_config(mocker):
    source = SourcePulseAwsIam()
    invalid_config = {
        "provider": {
            "auth_type": "invalid"
        }
    }
    success, error = source.check_connection(logger=None, config=invalid_config)
    assert success is False
    assert error is not None

def test_check_connection_fails_on_error(mocker, access_key_config):
    mock_iam_client = mocker.MagicMock()
    mock_iam_client.list_users.side_effect = Exception("Connection failed")

    mocker.patch('boto3.client', return_value=mock_iam_client)

    source = SourcePulseAwsIam()
    success, error = source.check_connection(logger=None, config=access_key_config)

    assert success is False
    assert error is not None
