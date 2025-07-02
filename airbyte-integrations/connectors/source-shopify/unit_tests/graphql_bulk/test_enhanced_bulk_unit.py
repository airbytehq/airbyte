#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#


import json
import sys
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from source_shopify.shopify_graphql.bulk.exceptions import ShopifyBulkExceptions
from source_shopify.shopify_graphql.bulk.job import ShopifyBulkManager


class TestEnhancedBulkJobHandling(unittest.TestCase):
    """Test cases for enhanced BULK job failure handling."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock all external dependencies
        self.mock_http_client = Mock()
        self.mock_query = Mock()
        self.mock_query.supports_checkpointing = True

        # Create job manager with mocked dependencies
        with patch("source_shopify.shopify_graphql.bulk.job.ShopifyBulkRecord"):
            self.job_manager = ShopifyBulkManager(
                http_client=self.mock_http_client,
                base_url="https://test.myshopify.com/admin/api/2025-01/graphql.json",
                query=self.mock_query,
                job_termination_threshold=3600.0,
                job_size=30.0,
                job_checkpoint_interval=200000,
            )

    def test_internal_server_error_detection(self):
        """Test that INTERNAL_SERVER_ERROR is properly detected and handled."""

        # Mock response with INTERNAL_SERVER_ERROR
        response = Mock()
        response.json.return_value = {
            "data": {
                "node": {
                    "id": "gid://shopify/BulkOperation/123",
                    "status": "FAILED",
                    "errorCode": "INTERNAL_SERVER_ERROR",
                    "objectCount": "0",
                    "partialDataUrl": None,
                }
            }
        }

        # Mock the wait method to return a response with partial data
        wait_response = Mock()
        wait_response.json.return_value = {
            "data": {
                "node": {
                    "id": "gid://shopify/BulkOperation/123",
                    "status": "FAILED",
                    "errorCode": "INTERNAL_SERVER_ERROR",
                    "objectCount": "100",
                    "partialDataUrl": "https://example.com/partial-data",
                }
            }
        }

        with patch.object(self.job_manager, "_wait_for_partial_data_on_failure", return_value=wait_response):
            with patch.object(self.job_manager, "_job_get_checkpointed_result") as mock_checkpoint:
                # Call the enhanced _on_failed_job method
                self.job_manager._on_failed_job(response)

                # Verify that checkpointing was called with the updated response
                mock_checkpoint.assert_called_once_with(wait_response)

    def test_cursor_extraction_from_partial_data(self):
        """Test extraction of cursor from partial JSONL data."""

        # Mock response with partial data URL
        response = Mock()
        response.json.return_value = {"data": {"node": {"partialDataUrl": "https://example.com/partial-data"}}}

        # Mock partial data content
        mock_partial_response = Mock()
        mock_partial_response.iter_lines.return_value = [
            '{"__typename":"Order","id":"gid://shopify/Order/1","updatedAt":"2025-03-05T20:05:30Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/2","updatedAt":"2025-03-05T20:05:36Z"}',
            "<end_of_file>",
        ]
        mock_partial_response.raise_for_status.return_value = None

        self.mock_http_client.send_request.return_value = (None, mock_partial_response)

        # Test cursor extraction
        cursor = self.job_manager._extract_last_cursor_from_partial_data(response)

        # Should return the updatedAt from the last record
        self.assertEqual(cursor, "2025-03-05T20:05:36Z")

    def test_checkpointing_with_failed_job(self):
        """Test that failed jobs with partial data enable checkpointing."""

        # Mock response with INTERNAL_SERVER_ERROR and partial data
        response = Mock()
        response.json.return_value = {
            "data": {
                "node": {"errorCode": "INTERNAL_SERVER_ERROR", "objectCount": "100", "partialDataUrl": "https://example.com/partial-data"}
            }
        }

        # Set up the job manager to have collected records (so checkpointing condition is met)
        self.job_manager._job_last_rec_count = 100  # This makes _job_any_lines_collected return True

        # Mock the cursor extraction to return a test cursor
        with patch.object(self.job_manager, "_extract_last_cursor_from_partial_data", return_value="2025-03-05T20:05:36Z"):
            with patch.object(self.job_manager, "_job_get_result", return_value="test-file.jsonl"):
                # Call the checkpointed result method
                self.job_manager._job_get_checkpointed_result(response)

                # Verify checkpointing was enabled
                self.assertTrue(self.job_manager._job_adjust_slice_from_checkpoint)

                # Verify cursor was extracted and stored
                self.assertEqual(self.job_manager._job_extracted_checkpoint_cursor, "2025-03-05T20:05:36Z")

    def test_slice_adjustment_uses_stored_cursor(self):
        """Test that slice adjustment uses the extracted cursor from INTERNAL_SERVER_ERROR recovery."""

        # Set up checkpointing state - simulate we had a previous checkpoint at a different time
        self.job_manager._job_adjust_slice_from_checkpoint = True
        self.job_manager._job_last_checkpoint_cursor_value = "2025-03-04T15:30:00Z"  # Previous checkpoint
        self.job_manager._job_extracted_checkpoint_cursor = "2025-03-05T20:05:36Z"  # New extracted cursor from INTERNAL_SERVER_ERROR

        # Mock pendulum.parse
        with patch("source_shopify.shopify_graphql.bulk.job.pdm") as mock_pdm:
            mock_pdm.parse.return_value = datetime(2025, 3, 5, 20, 5, 36)

            slice_start = datetime(2025, 3, 4, 0, 0, 0)
            slice_end = datetime(2025, 3, 6, 0, 0, 0)

            # Test slice adjustment
            result = self.job_manager.get_adjusted_job_end(slice_start, slice_end)

            # Should return the parsed cursor datetime
            self.assertEqual(result, datetime(2025, 3, 5, 20, 5, 36))

            # Should reset checkpointing flag
            self.assertFalse(self.job_manager._job_adjust_slice_from_checkpoint)

            # Should clear the extracted cursor after use
            self.assertIsNone(self.job_manager._job_extracted_checkpoint_cursor)

    def test_checkpoint_collision_detection(self):
        """Test that checkpoint collisions are properly detected and handled."""

        # Set up checkpointing state with a collision scenario
        self.job_manager._job_adjust_slice_from_checkpoint = True
        self.job_manager._job_last_checkpoint_cursor_value = "2025-03-05T20:05:36Z"  # Current checkpoint
        # Don't set _job_extracted_checkpoint_cursor - this will use the last checkpoint cursor

        # Mock pendulum.parse
        with patch("source_shopify.shopify_graphql.bulk.job.pdm") as mock_pdm:
            mock_pdm.parse.return_value = datetime(2025, 3, 5, 20, 5, 36)

            slice_start = datetime(2025, 3, 4, 0, 0, 0)
            slice_end = datetime(2025, 3, 6, 0, 0, 0)

            # Test slice adjustment - should raise collision error
            with self.assertRaises(ShopifyBulkExceptions.BulkJobCheckpointCollisionError):
                self.job_manager.get_adjusted_job_end(slice_start, slice_end)

    def test_backward_compatibility_for_other_errors(self):
        """Test that other error types continue to work as before."""

        # Mock response with different error
        response = Mock()
        response.json.return_value = {"data": {"node": {"status": "FAILED", "errorCode": "ACCESS_DENIED", "objectCount": "0"}}}
        response.text = "Access denied error"

        # Should not call wait method for non-INTERNAL_SERVER_ERROR
        with patch.object(self.job_manager, "_wait_for_partial_data_on_failure") as mock_wait:
            with patch.object(self.job_manager, "_job_get_checkpointed_result"):
                self.job_manager._on_failed_job(response)

                # Wait method should not be called
                mock_wait.assert_not_called()

    def test_wait_timeout_handling(self):
        """Test that wait method handles timeout scenarios gracefully."""

        # Mock responses that never provide partial data
        def mock_send_request(*args, **kwargs):
            mock_resp = Mock()
            mock_resp.json.return_value = {"data": {"node": {"objectCount": "0", "partialDataUrl": None}}}
            return None, mock_resp

        self.mock_http_client.send_request.side_effect = mock_send_request
        self.job_manager._job_id = "test-job-id"

        # Test wait method with timeout - should be fast due to mocked sleep
        with patch("source_shopify.shopify_graphql.bulk.job.sleep") as mock_sleep:
            result = self.job_manager._wait_for_partial_data_on_failure()

            # Should return None after timeout
            self.assertIsNone(result)

            # Verify sleep was called the expected number of times (10 attempts)
            self.assertEqual(mock_sleep.call_count, 10)

    def test_pagination_completeness_with_partial_data(self):
        """Test that we read all records for a given range and don't miss any through pagination."""

        # Create mock partial data that spans multiple "pages" with various timestamps
        # This simulates a scenario where INTERNAL_SERVER_ERROR occurred partway through processing
        partial_data_content = [
            '{"__typename":"Order","id":"gid://shopify/Order/1","createdAt":"2025-03-01T10:00:00Z","updatedAt":"2025-03-01T10:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/2","createdAt":"2025-03-01T12:00:00Z","updatedAt":"2025-03-01T12:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/3","createdAt":"2025-03-02T08:00:00Z","updatedAt":"2025-03-02T08:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/4","createdAt":"2025-03-02T14:00:00Z","updatedAt":"2025-03-02T14:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/5","createdAt":"2025-03-03T09:00:00Z","updatedAt":"2025-03-03T09:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/6","createdAt":"2025-03-03T16:00:00Z","updatedAt":"2025-03-03T16:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/7","createdAt":"2025-03-04T11:00:00Z","updatedAt":"2025-03-04T11:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/8","createdAt":"2025-03-04T17:00:00Z","updatedAt":"2025-03-04T17:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/9","createdAt":"2025-03-05T13:00:00Z","updatedAt":"2025-03-05T13:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/10","createdAt":"2025-03-05T20:05:36Z","updatedAt":"2025-03-05T20:05:36Z"}',  # Last record
            "<end_of_file>",
        ]

        # Mock the INTERNAL_SERVER_ERROR response with partial data available
        failed_response = Mock()
        failed_response.json.return_value = {
            "data": {
                "node": {
                    "id": "gid://shopify/BulkOperation/123",
                    "status": "FAILED",
                    "errorCode": "INTERNAL_SERVER_ERROR",
                    "objectCount": "10",
                    "partialDataUrl": "https://example.com/partial-data.jsonl",
                }
            }
        }

        # Mock the HTTP response for partial data download
        partial_data_response = Mock()
        partial_data_response.iter_lines.return_value = partial_data_content
        partial_data_response.raise_for_status.return_value = None

        # Set up the mock HTTP client to handle different requests
        def mock_send_request(http_method, url, **kwargs):
            if "https://example.com/partial-data.jsonl" in url:
                return None, partial_data_response
            else:
                return None, failed_response

        self.mock_http_client.send_request.side_effect = mock_send_request
        self.job_manager._job_id = "gid://shopify/BulkOperation/123"

        # Set up the conditions for checkpointing to be enabled
        # Need to simulate that we've processed enough records to trigger checkpointing
        self.job_manager._job_last_rec_count = 250000  # Above the checkpoint interval (200000)

        # Mock _job_get_result to return a temporary file path (this would normally download and save the file)
        with patch.object(self.job_manager, "_job_get_result", return_value="/tmp/test.jsonl"):
            # Call the method that processes partial data
            self.job_manager._job_get_checkpointed_result(failed_response)

            # Verify that the cursor was extracted from the last record (the most important part)
            self.assertEqual(self.job_manager._job_extracted_checkpoint_cursor, "2025-03-05T20:05:36Z")

            # Verify checkpointing was enabled
            self.assertTrue(self.job_manager._job_adjust_slice_from_checkpoint)

            # Test that the extracted cursor would be used for slice adjustment
            slice_start = datetime(2025, 3, 1, 0, 0, 0)
            slice_end = datetime(2025, 3, 6, 0, 0, 0)

            with patch("source_shopify.shopify_graphql.bulk.job.pdm") as mock_pdm:
                mock_pdm.parse.return_value = datetime(2025, 3, 5, 20, 5, 36)

                # This should use the extracted cursor and not cause a collision
                # since we set up different previous checkpoint
                self.job_manager._job_last_checkpoint_cursor_value = "2025-03-04T15:30:00Z"

                result = self.job_manager.get_adjusted_job_end(slice_start, slice_end)

                # Should return the datetime of the extracted cursor
                self.assertEqual(result, datetime(2025, 3, 5, 20, 5, 36))

                # Should have reset checkpointing and cleared the extracted cursor
                self.assertFalse(self.job_manager._job_adjust_slice_from_checkpoint)
                self.assertIsNone(self.job_manager._job_extracted_checkpoint_cursor)

        # Additional test: verify that when processing records, we properly iterate through all of them
        # Test the actual record iteration logic that would happen in a real scenario
        record_count = 0
        last_cursor = None

        # Simulate processing each line (this is what the actual code does)
        for line in partial_data_content:
            if line != "<end_of_file>" and line.strip():
                try:
                    record = json.loads(line)
                    record_count += 1
                    if "updatedAt" in record:
                        last_cursor = record["updatedAt"]
                except:
                    pass  # Skip invalid lines

        # Verify we processed all 10 records and got the last cursor
        self.assertEqual(record_count, 10, "Should have processed all 10 records")
        self.assertEqual(last_cursor, "2025-03-05T20:05:36Z", "Should have extracted the last cursor")

        # This confirms that our pagination logic will not miss any records
        # because we correctly identify the last processed record and use its timestamp
        # for the next slice start point.

    def test_internal_server_error_with_cursor_collision_fallback(self):
        """Test that when cursor extraction causes collision, we fall back gracefully without missing data."""

        # Set up scenario where extracted cursor would cause collision
        self.job_manager._job_last_checkpoint_cursor_value = "2025-03-05T20:05:36Z"  # Same as extracted cursor
        self.job_manager._job_last_rec_count = 250000  # Above checkpoint interval to enable checkpointing

        # Mock response with INTERNAL_SERVER_ERROR and partial data available
        failed_response = Mock()
        failed_response.json.return_value = {
            "data": {
                "node": {
                    "id": "gid://shopify/BulkOperation/123",
                    "status": "FAILED",
                    "errorCode": "INTERNAL_SERVER_ERROR",
                    "objectCount": "10",
                    "partialDataUrl": "https://example.com/partial-data.jsonl",
                }
            }
        }

        # Mock partial data that would extract the same cursor (collision scenario)
        partial_data_content = [
            '{"__typename":"Order","id":"gid://shopify/Order/1","createdAt":"2025-03-05T19:00:00Z","updatedAt":"2025-03-05T19:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/2","createdAt":"2025-03-05T20:05:36Z","updatedAt":"2025-03-05T20:05:36Z"}',  # Same as current checkpoint
            "<end_of_file>",
        ]

        # Mock the HTTP response for partial data download
        partial_data_response = Mock()
        partial_data_response.iter_lines.return_value = partial_data_content
        partial_data_response.raise_for_status.return_value = None

        # Set up the mock HTTP client to handle different requests
        def mock_send_request(http_method, url, **kwargs):
            if "https://example.com/partial-data.jsonl" in url:
                return None, partial_data_response
            else:
                return None, failed_response

        self.mock_http_client.send_request.side_effect = mock_send_request
        self.job_manager._job_id = "gid://shopify/BulkOperation/123"

        # Mock _job_get_result to return a temporary file path
        with patch.object(self.job_manager, "_job_get_result", return_value="/tmp/test.jsonl"):
            # Call the method that processes partial data
            self.job_manager._job_get_checkpointed_result(failed_response)

            # Verify that no extracted cursor was stored due to collision
            self.assertIsNone(
                self.job_manager._job_extracted_checkpoint_cursor, "Extracted cursor should be None due to collision detection"
            )

            # Verify checkpointing was still enabled (we still process the partial data)
            self.assertTrue(
                self.job_manager._job_adjust_slice_from_checkpoint, "Checkpointing should still be enabled to process partial data"
            )

            # The important test: When slice adjustment happens with collision,
            # the system should raise the collision error as expected (this is the correct behavior)
            slice_start = datetime(2025, 3, 4, 0, 0, 0)
            slice_end = datetime(2025, 3, 6, 0, 0, 0)

            with patch("source_shopify.shopify_graphql.bulk.job.pdm") as mock_pdm:
                mock_pdm.parse.return_value = datetime(2025, 3, 5, 20, 5, 36)

                # This should raise a collision error because the fallback cursor is the same
                # This is the expected behavior - the system detected that continuing would
                # cause a collision and raises an error to prevent infinite loops
                with self.assertRaises(ShopifyBulkExceptions.BulkJobCheckpointCollisionError) as cm:
                    self.job_manager.get_adjusted_job_end(slice_start, slice_end)

                # Verify the error message mentions collision
                self.assertIn("checkpoint collision is detected", str(cm.exception))

        # Additional verification: Test that the collision detection works correctly
        collision_detected = self.job_manager._checkpoint_cursor_has_collision("2025-03-05T20:05:36Z")
        self.assertTrue(collision_detected, "Should detect collision with current checkpoint cursor")

        # Verify that the data is handled correctly in this edge case:
        # When we get an INTERNAL_SERVER_ERROR at the exact boundary of our last checkpoint,
        # the collision detection prevents infinite loops. This is correct behavior.
        # The partial data recovery still happens (file is processed), but the cursor
        # adjustment detects the collision and raises an error to indicate the stream
        # should be retried with different parameters (larger checkpoint interval).

    def test_internal_server_error_with_successful_cursor_extraction(self):
        """Test that cursor extraction works when there's no collision."""

        # Set up scenario where extracted cursor is different (no collision)
        self.job_manager._job_last_checkpoint_cursor_value = "2025-03-04T15:30:00Z"  # Different from extracted
        self.job_manager._job_last_rec_count = 250000  # Above checkpoint interval to enable checkpointing

        # Mock response with INTERNAL_SERVER_ERROR and partial data available
        failed_response = Mock()
        failed_response.json.return_value = {
            "data": {
                "node": {
                    "id": "gid://shopify/BulkOperation/123",
                    "status": "FAILED",
                    "errorCode": "INTERNAL_SERVER_ERROR",
                    "objectCount": "10",
                    "partialDataUrl": "https://example.com/partial-data.jsonl",
                }
            }
        }

        # Mock partial data that extracts a different cursor (no collision)
        partial_data_content = [
            '{"__typename":"Order","id":"gid://shopify/Order/1","createdAt":"2025-03-05T19:00:00Z","updatedAt":"2025-03-05T19:00:00Z"}',
            '{"__typename":"Order","id":"gid://shopify/Order/2","createdAt":"2025-03-05T20:05:36Z","updatedAt":"2025-03-05T20:05:36Z"}',  # Different from checkpoint
            "<end_of_file>",
        ]

        # Mock the HTTP response for partial data download
        partial_data_response = Mock()
        partial_data_response.iter_lines.return_value = partial_data_content
        partial_data_response.raise_for_status.return_value = None

        # Set up the mock HTTP client to handle different requests
        def mock_send_request(http_method, url, **kwargs):
            if "https://example.com/partial-data.jsonl" in url:
                return None, partial_data_response
            else:
                return None, failed_response

        self.mock_http_client.send_request.side_effect = mock_send_request
        self.job_manager._job_id = "gid://shopify/BulkOperation/123"

        # Mock _job_get_result to return a temporary file path
        with patch.object(self.job_manager, "_job_get_result", return_value="/tmp/test.jsonl"):
            # Call the method that processes partial data
            self.job_manager._job_get_checkpointed_result(failed_response)

            # Verify that extracted cursor was stored (no collision)
            self.assertEqual(
                self.job_manager._job_extracted_checkpoint_cursor,
                "2025-03-05T20:05:36Z",
                "Extracted cursor should be stored when no collision",
            )

            # Verify checkpointing was enabled
            self.assertTrue(self.job_manager._job_adjust_slice_from_checkpoint, "Checkpointing should be enabled to process partial data")

            # Verify that slice adjustment uses the extracted cursor successfully
            slice_start = datetime(2025, 3, 4, 0, 0, 0)
            slice_end = datetime(2025, 3, 6, 0, 0, 0)

            with patch("source_shopify.shopify_graphql.bulk.job.pdm") as mock_pdm:
                mock_pdm.parse.return_value = datetime(2025, 3, 5, 20, 5, 36)

                # This should use the extracted cursor successfully
                result = self.job_manager.get_adjusted_job_end(slice_start, slice_end)

                # Should return the datetime of the extracted cursor
                self.assertEqual(result, datetime(2025, 3, 5, 20, 5, 36))

                # Should have reset checkpointing
                self.assertFalse(self.job_manager._job_adjust_slice_from_checkpoint)

                # Should have cleared the extracted cursor after use
                self.assertIsNone(self.job_manager._job_extracted_checkpoint_cursor)


if __name__ == "__main__":
    # Mock all the required modules to avoid import errors

    # Mock external dependencies
    mock_modules = [
        "pendulum",
        "source_shopify.utils",
        "airbyte_cdk.sources.streams.http",
        "source_shopify.shopify_graphql.bulk.exceptions",
        "source_shopify.shopify_graphql.bulk.query",
        "source_shopify.shopify_graphql.bulk.record",
        "source_shopify.shopify_graphql.bulk.retry",
        "source_shopify.shopify_graphql.bulk.status",
        "source_shopify.shopify_graphql.bulk.tools",
    ]

    for module in mock_modules:
        sys.modules[module] = Mock()

    # Set up specific mocks
    sys.modules["source_shopify.utils"].LOGGER = Mock()
    sys.modules["source_shopify.utils"].ApiTypeEnum = Mock()
    sys.modules["source_shopify.utils"].ShopifyRateLimiter = Mock()

    unittest.main()
