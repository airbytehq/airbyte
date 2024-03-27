#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
import unittest
from http import HTTPStatus

import requests
import requests_mock
from source_zoom.components import ServerToServerOauthAuthenticator


class TestOAuthClient(unittest.TestCase):
    def test_generate_access_token(self):
        except_access_token = "rc-test-token"
        except_token_response = {"access_token": except_access_token}

        config = {
            "account_id": "rc-asdfghjkl",
            "client_id": "rc-123456789",
            "client_secret": "rc-test-secret",
            "authorization_endpoint": "https://example.zoom.com/oauth/token"
        }
        parameters = config
        client = ServerToServerOauthAuthenticator(
            config=config,
            account_id=config["account_id"],
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            authorization_endpoint=config["authorization_endpoint"],
            parameters=parameters,
        )

        # Encode the client credentials in base64
        token = base64.b64encode(f'{config.get("client_id")}:{config.get("client_secret")}'.encode("ascii")).decode("utf-8")

        # Define the headers that should be sent in the request
        headers = {"Authorization": f"Basic {token}", "Content-type": "application/json"}

        # Define the URL containing the grant_type and account_id as query parameters
        url = f'{config.get("authorization_endpoint")}?grant_type=account_credentials&account_id={config.get("account_id")}'

        with requests_mock.Mocker() as m:
            # Mock the requests.post call with the expected URL, headers and token response
            m.post(url, json=except_token_response, request_headers=headers, status_code=HTTPStatus.OK)

            # Call the generate_access_token function and assert it returns the expected access token
            self.assertEqual(client.generate_access_token(), except_access_token)

        # Test case when the endpoint has some error, like a timeout
        with requests_mock.Mocker() as m:
            m.post(url, exc=requests.exceptions.RequestException)
            with self.assertRaises(Exception) as cm:
                client.generate_access_token()
            self.assertIn("Error while generating access token", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
