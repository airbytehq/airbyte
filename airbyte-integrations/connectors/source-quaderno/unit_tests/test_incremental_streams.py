#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import unittest

from source_quaderno.streams import IncrementalQuadernoStream


class TestIncrementalQuadernoStream(unittest.TestCase):

    def setUp(self):
        # Initialize the TestIncrementalQuadernoStream class with mock configuration data
        config = {
            'account_name': 'test_account',
            'start_date': '2023-01-01',
        }
        self.stream = IncrementalQuadernoStream(config=config)

    def test_cursor_field(self):
        # By default, the cursor_field should be "id"
        self.assertEqual(self.stream.cursor_field, "id")

    def test_supports_incremental(self):
        self.assertTrue(self.stream.supports_incremental)

    def test_source_defined_cursor(self):
        self.assertTrue(self.stream.source_defined_cursor)

    def test_stream_checkpoint_interval(self):
        self.assertIsNone(self.stream.state_checkpoint_interval)

    def test_get_updated_state(self):
        # Define a sample record and current state
        latest_record = {"id": 100, "number": "004321", "issue_date": "2023-06-30"}
        current_state = {"id": 50, "number": "001234", "issue_date": "2023-01-31"}

        # Call the get_updated_state method
        updated_state = self.stream.get_updated_state(current_state, latest_record)

        # Assertions
        self.assertEqual(updated_state, {"id": 50})

    def test_get_updated_state_empty_state(self):
        # If the current state is empty, the cursor from the latest record should be picked
        latest_record = {"id": 100, 'name': 'John Doe'}
        current_state = {}

        # Call the get_updated_state method
        updated_state = self.stream.get_updated_state(current_state, latest_record)

        # Assertions
        self.assertEqual(updated_state, {"id": 100})

    def test_get_updated_state_latest_record_older_than_current_state(self):
        # If the latest_record is older (smaller) than the current state, the current state should remain unchanged
        latest_record = {"id": 50, "number": "001234", "issue_date": "2023-01-31"}
        current_state = {"id": 100, "number": "004321", "issue_date": "2023-06-30"}

        # Call the get_updated_state method
        updated_state = self.stream.get_updated_state(current_state, latest_record)

        # Assertions
        self.assertEqual(updated_state, {"id": 50})
