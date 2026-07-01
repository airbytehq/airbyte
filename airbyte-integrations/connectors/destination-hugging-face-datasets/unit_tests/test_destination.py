#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import unittest
from unittest.mock import MagicMock, patch

from destination_hugging_face_datasets.destination import DestinationHuggingFaceDatasets

from airbyte_cdk.models import Status


class TestDestinationHuggingFaceDatasetsCheck(unittest.TestCase):
    """Tests for the DestinationHuggingFaceDatasets.check method."""

    def setUp(self):
        self.destination = DestinationHuggingFaceDatasets()

    def test_check_dataset_name_required(self):
        """Test that dataset_name is required."""
        config = {
            "token": "hf_test",
        }

        result = self.destination.check(MagicMock(), config)
        self.assertEqual(result.status, Status.FAILED)

    @patch("destination_hugging_face_datasets.destination.HfApi")
    def test_check_hub_success(self, mock_api):
        """Test successful Hub connection check."""
        mock_api.return_value = MagicMock()

        config = {
            "dataset_name": "test/dataset",
            "token": "hf_test",
        }

        result = self.destination.check(MagicMock(), config)
        self.assertEqual(result.status, Status.SUCCEEDED)

    @patch("destination_hugging_face_datasets.destination.HfApi")
    def test_check_hub_failure(self, mock_api):
        """Test failed Hub connection check."""
        mock_instance = MagicMock()
        mock_api.return_value = mock_instance
        mock_instance.create_branch.side_effect = Exception("Invalid token")

        config = {
            "dataset_name": "test/dataset",
            "token": "hf_test",
        }

        result = self.destination.check(MagicMock(), config)
        self.assertEqual(result.status, Status.FAILED)


class TestDestinationHuggingFaceDatasetsWrite(unittest.TestCase):
    """Tests for the DestinationHuggingFaceDatasets.write method."""

    def setUp(self):
        self.destination = DestinationHuggingFaceDatasets()

    def test_write_requires_dataset_name(self):
        """Test that dataset_name is required."""
        config = {
            "push_to_hub": True,
            "token": "hf_test",
        }

        with self.assertRaises(ValueError) as context:
            list(self.destination.write(config, MagicMock(), iter([])))
        self.assertIn("dataset_name is required", str(context.exception))

    @patch("destination_hugging_face_datasets.destination.Dataset")
    def test_write(self, mock_dataset):
        """Test successful push to Hub."""
        # Mock Dataset
        mock_dataset_instance = MagicMock()
        mock_dataset.from_pandas.return_value = mock_dataset_instance

        # Create mock messages
        from airbyte_cdk.models import AirbyteMessage, AirbyteRecordMessage, Type
        messages = [
            AirbyteMessage(
                type=Type.RECORD,
                record=AirbyteRecordMessage(
                    data={"col1": "value1", "col2": 123},
                    stream="test_stream",
                    emitted_at=0,
                )
            ),
            AirbyteMessage(type=Type.STATE, state={"checkpoint": 1}),
        ]

        config = {
            "dataset_name": "test/dataset",
            "token": "hf_test",
        }

        result = list(self.destination.write(config, MagicMock(), iter(messages)))

        # Verify push_to_hub was called
        mock_dataset_instance.push_to_hub.assert_called_once_with("test/dataset", "test_stream", token="hf_test")

        # Verify state message was yielded
        state_messages = [m for m in result if m.type == Type.STATE]
        self.assertEqual(len(state_messages), 1)


if __name__ == "__main__":
    unittest.main()