#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import Mock, patch

from source_quaderno.source import SourceQuaderno


class TestSourceQuaderno(unittest.TestCase):

    def setUp(self):
        # Initialize the SourceQuaderno class with a mock logger
        self.logger = Mock()
        self.source = SourceQuaderno()

    def test_check_connection_successful(self):
        # Mock requests.get to return a successful response
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'identity': {'href': 'https://account_name.quadernoapp.com/api/'}
            }

            # Provide mock configuration data
            config = {
                'api_key': 'VALID_API_KEY',
                'account_name': 'account_name'
            }

            # Call the check_connection method
            result, error = self.source.check_connection(self.logger, config)

            # Assertions
            self.assertTrue(result)
            self.assertIsNone(error)
            self.logger.debug.assert_called_with("Connection to Quaderno was successful.")

    def test_check_connection_unsuccessful(self):
        # Mock requests.get to return an unsuccessful response
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 401
            mock_get.return_value.json.return_value = {'error': 'Unauthorized'}

            # Provide mock configuration data
            config = {
                'api_key': 'INVALID_API_KEY',
                'account_name': 'account_name'
            }

            # Call the check_connection method
            result, error = self.source.check_connection(self.logger, config)

            # Assertions
            self.assertFalse(result)
            self.assertEqual(error, "Authorization failed with status code 401. Error message: Unauthorized")
            self.logger.info.assert_called_with("Connection to Quaderno was unsuccessful with status code 401.")

    def test_check_connection_api_key_not_authorized(self):
        # Mock requests.get to return a successful response, but with an incorrect account_name
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {
                'identity': {'href': 'https://other_account.quadernoapp.com/api/'}
            }

            # Provide mock configuration data
            config = {
                'api_key': 'UNAUTHORIZED_API_KEY',
                'account_name': 'account_name'
            }

            # Call the check_connection method
            result, error = self.source.check_connection(self.logger, config)

            # Assertions
            self.assertFalse(result)
            self.assertEqual(error, "The API Key is not authorized for the account.")
            self.logger.info.assert_called_with(
                "Connection to Quaderno was unsuccessful. The API Key is not authorized for the account."
            )

    def test_streams(self):
        # Provide mock configuration data
        config = {
            'api_key': 'YOUR_API_KEY',
            'account_name': 'account_name'
        }

        # Call the streams method
        streams = self.source.streams(config)

        # Assertions
        self.assertIsInstance(streams, list)
        self.assertEqual(len(streams), 3)
