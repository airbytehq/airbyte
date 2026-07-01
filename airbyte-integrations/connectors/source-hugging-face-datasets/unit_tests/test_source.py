"""Unit tests for the Hugging Face Datasets source connector."""

import logging
from unittest.mock import patch

import pytest
from source_hugging_face_datasets.source import SourceHuggingFaceDatasets

from airbyte_cdk.models import (
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    Status,
    SyncMode,
    Type,
)


@pytest.fixture
def source():
    """Create a source instance."""
    return SourceHuggingFaceDatasets()


@pytest.fixture
def config():
    """Create a test configuration."""
    return {
        "dataset_name": "squad",
        "dataset_subsets": [],
        "dataset_splits": [],
        "token": None,
    }


@pytest.fixture
def logger():
    """Create a logger."""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.WARNING)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    return logger


class TestSourceHuggingFaceDatasetsCheck:
    """Test the check connection method."""

    def test_check_connection_success(self, source, config, logger):
        """Test successful connection check."""
        with patch("datasets.get_dataset_config_names") as mock_get_configs:
            mock_get_configs.return_value = ["default"]
            result = source.check(logger, config)
            assert result.status == Status.SUCCEEDED

    def test_check_connection_failure(self, source, config, logger):
        """Test failed connection check."""
        with patch("datasets.get_dataset_config_names") as mock_get_configs:
            mock_get_configs.side_effect = Exception("Dataset not found")
            result = source.check(logger, config)
            assert result.status == Status.FAILED


class TestSourceHuggingFaceDatasetsDiscover:
    """Test the discover method."""

    def test_discover_creates_streams(self, source, config, logger):
        """Test that discover creates streams for each config and split."""
        with patch("datasets.get_dataset_config_names") as mock_get_configs, \
             patch("datasets.get_dataset_split_names") as mock_get_splits:
            
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train", "test"]
            
            catalog = source.discover(logger, config)
            
            assert len(catalog.streams) == 2
            assert any("squad" in s.name for s in catalog.streams)


class TestSourceHuggingFaceDatasetsRead:
    """Test the read method."""

    def test_read(self, source, config, logger):
        """Test that read returns records from the dataset."""
        # Mock the dataset
        mock_dataset = [
            {"id": "1", "context": "Some context"},
            {"id": "2", "context": "Another context"},
        ]

        with patch("datasets.get_dataset_config_names") as mock_get_configs, \
             patch("datasets.get_dataset_split_names") as mock_get_splits, \
             patch("datasets.load_dataset") as mock_load_dataset:
            
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train"]
            mock_load_dataset.return_value = mock_dataset
            
            # Create a simple catalog with required sync_mode and destination_sync_mode
            stream = AirbyteStream(
                name="squad__default__train",
                json_schema={"type": "object", "additionalProperties": True},
                supported_sync_modes=[SyncMode.full_refresh],
            )
            catalog = ConfiguredAirbyteCatalog(
                streams=[ConfiguredAirbyteStream(
                    stream=stream,
                    sync_mode=SyncMode.full_refresh,
                    destination_sync_mode=DestinationSyncMode.append,
                )]
            )
            
            messages = list(source.read(logger, config, catalog))
            records = [m for m in messages if m.type == Type.RECORD]
            assert len(records) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
