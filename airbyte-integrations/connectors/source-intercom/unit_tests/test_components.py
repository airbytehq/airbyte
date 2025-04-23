import unittest
from unittest.mock import patch, MagicMock
import requests
import json
import yaml
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
import os
import pytest
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Existing test_rate_limiter test
@pytest.mark.parametrize(
    "rate_limit_header, backoff_time",
    [
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 167}, 0.01),
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 100}, 0.01),
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 83}, 1.5),
        ({"X-RateLimit-Limit": 167, "X-RateLimit-Remaining": 16}, 8.0),
        ({}, 1.0),
    ],
)
def test_rate_limiter(components_module, rate_limit_header, backoff_time):
    IntercomRateLimiter = components_module.IntercomRateLimiter

    def check_backoff_time(t):
        """A replacer for original `IntercomRateLimiter.backoff_time`"""
        assert backoff_time == t, f"Expected {backoff_time}, got {t}"

    class Requester:
        @IntercomRateLimiter.balance_rate_limit()
        def interpret_response_status(self, response: requests.Response):
            """A stub for the decorator function being tested"""

    with patch.object(IntercomRateLimiter, "backoff_time") as backoff_time_mock:
        # Call `check_backoff_time` instead of original `IntercomRateLimiter.backoff_time` method
        backoff_time_mock.side_effect = check_backoff_time

        requester = Requester()

        # Prepare requester object with headers
        response = requests.models.Response()
        response.headers = rate_limit_header

        # Call a decorated method
        requester.interpret_response_status(response)

# Test class for Companies stream retry behavior
class TestCompaniesStreamRetryFromFirstPage(unittest.TestCase):
    def setUp(self):
        # Locate and load the existing manifest.yaml file
        manifest_path = os.path.join(os.path.dirname(__file__), '..', 'manifest.yaml')
        if not os.path.exists(manifest_path):
            self.fail(f"manifest.yaml not found at expected path: {manifest_path}")
        
        with open(manifest_path, 'r') as file:
            self.manifest = yaml.safe_load(file)

        # Prepare mock HTTP responses for the Companies stream
        self.mock_responses = [
            # First attempt: 500 error on first page
            {
                "status_code": 500,
                "json": {}
            },
            # Retry: successful first page
            {
                "status_code": 200,
                "json": {
                    "data": [{"id": "1", "name": "Company 1"}],
                    "scroll_param": "token1"
                }
            },
            # Second page: successful
            {
                "status_code": 200,
                "json": {
                    "data": [{"id": "2", "name": "Company 2"}],
                    "scroll_param": "token2"
                }
            },
            # Third page: successful with no more data (empty data list)
            {
                "status_code": 200,
                "json": {
                    "data": [],
                    "scroll_param": None
                }
            }
        ]
        self.response_index = 0

    def test_retry_from_first_page_on_500_error(self):
        # Define mock_send_request to properly simulate requests.Session.send
        def mock_send_request(request, **kwargs):
            logger.debug(f"Mocking request to {request.url}")
            if self.response_index >= len(self.mock_responses):
                self.fail(f"Unexpected request made beyond mock responses: index {self.response_index}")
    
            response_data = self.mock_responses[self.response_index]
            response = requests.Response()
            response.status_code = response_data["status_code"]
            response._content = json.dumps(response_data["json"]).encode('utf-8')
            response.headers = {}  # Default empty headers if not specified
            response.request = request  # Attach the original request to the response
    
            # Create a mock raw response to satisfy requests_cache
            raw_mock = MagicMock()
            raw_mock._request_url = request.url  # Set the request URL
            response.raw = raw_mock  # Attach the mock raw response
    
            self.response_index += 1
            return response

        with patch('requests.Session.send', side_effect=mock_send_request):
            # Initialize the source with the loaded manifest
            source = ManifestDeclarativeSource(self.manifest)
            
            # Basic config (adjust based on your manifest's requirements)
            config = {"access_token": "dummy_token", "start_date": "2020-01-01T00:00:00Z"}
            catalog = {"streams": [{"name": "companies"}]}

            # Get the Companies stream
            try:
                stream = next(s for s in source.streams(config) if s.name == "companies")
            except StopIteration:
                self.fail("Companies stream not found in the manifest")

            # Read records and test error handling
            records = list(stream.read_records(sync_mode="full_refresh"))

            # Assertions to verify behavior
            self.assertEqual(len(records), 2, f"Expected 2 records after retry, got {len(records)}")
            self.assertEqual(records[0]["id"], "1", "First record ID mismatch")
            self.assertEqual(records[1]["id"], "2", "Second record ID mismatch")
            
            # Verify retry behavior (4 requests: initial Page 1 failure, retry Page 1 success, Page 2, Page 3 with empty data)
            self.assertEqual(self.response_index, 4, f"Expected 4 requests (including retries), got {self.response_index}")

if __name__ == '__main__':
    unittest.main()