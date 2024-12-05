#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, patch

from source_avni.components import CustomAuthenticator


@patch('boto3.client')
def test_token_property(mock_boto3_client):

    mock_cognito_client = Mock()
    mock_boto3_client.return_value = mock_cognito_client

    config= { "username": "example@gmail.com", "api_key": "api_key" }
    source = CustomAuthenticator(config=config,username="example@gmail.com",password="api_key",parameters="")
    source._username = Mock()
    source._username.eval.return_value = "test_username"
    source._password = Mock()
    source._password.eval.return_value = "test_password"
    source.get_client_id = Mock()
    source.get_client_id.return_value = "test_client_id"

    mock_cognito_client.initiate_auth.return_value = {
        "AuthenticationResult": {
            "IdToken": "test_id_token"
        }
    }
    token = source.token
    mock_boto3_client.assert_called_once_with("cognito-idp", region_name="ap-south-1")
    mock_cognito_client.initiate_auth.assert_called_once_with(
        ClientId="test_client_id",
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": "test_username", "PASSWORD": "test_password"}
    )
    assert token == "test_id_token"

def test_get_client_id(mocker):
    
    config= { "username": "example@gmail.com", "api_key": "api_key" }
    source = CustomAuthenticator(config=config,username="example@gmail.com",password="api_key",parameters="")
    client_id = source.get_client_id()
    expected_length = 26
    assert len(client_id) == expected_length