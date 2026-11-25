# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

"""Unit tests for the Hugging Face Datasets source connector."""

import base64
import importlib.util
import json
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import datasets
import numpy as np
import pytest
from source_hugging_face_datasets.source import SourceHuggingFaceDatasets, StreamSpec

from airbyte_cdk.models import (
    AirbyteStream,
    AirbyteStreamStatus,
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


def make_catalog(*stream_names):
    """Build a configured catalog with one full refresh stream per name."""
    return ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream(
                    name=name,
                    json_schema={"type": "object", "additionalProperties": True},
                    supported_sync_modes=[SyncMode.full_refresh],
                ),
                sync_mode=SyncMode.full_refresh,
                destination_sync_mode=DestinationSyncMode.append,
            )
            for name in stream_names
        ]
    )


def features(**columns):
    """Build a `datasets` features dict, e.g. features(id=Value("string"))."""
    return datasets.Features(columns)


class TestSpec:
    """Test the connector specification."""

    def test_token_is_a_secret(self, source, logger):
        """Test that both token fields are declared as secrets."""
        properties = source.spec(logger).connectionSpecification["properties"]
        assert properties["token"]["airbyte_secret"] is True
        assert properties["api_token"]["airbyte_secret"] is True

    def test_documentation_url(self, source, logger):
        """Test the documentation URL points to the source page."""
        assert source.spec(logger).documentationUrl == "https://docs.airbyte.com/integrations/sources/hugging-face-datasets"

    def test_spec_json_matches_the_python_spec(self, source, logger):
        """Test that the shipped spec.json does not drift from the spec returned by the connector."""
        spec_path = Path(__file__).parent.parent / "source_hugging_face_datasets" / "spec.json"
        spec_from_file = json.loads(spec_path.read_text())
        python_spec = source.spec(logger)

        assert spec_from_file["properties"] == python_spec.connectionSpecification["properties"]
        assert spec_from_file["required"] == python_spec.connectionSpecification["required"]
        assert spec_from_file["documentationUrl"] == python_spec.documentationUrl

    def test_get_token_falls_back_on_the_legacy_field(self):
        """Test that connections configured before 0.1.0 still authenticate."""
        assert SourceHuggingFaceDatasets._get_token({"token": "new"}) == "new"
        assert SourceHuggingFaceDatasets._get_token({"api_token": "legacy"}) == "legacy"
        assert SourceHuggingFaceDatasets._get_token({"token": "new", "api_token": "legacy"}) == "new"
        assert SourceHuggingFaceDatasets._get_token({}) is None

    def test_check_uses_the_legacy_token(self, source, logger):
        """Test that check passes the legacy token to the Hub."""
        with patch("datasets.get_dataset_config_names") as mock_get_configs:
            mock_get_configs.return_value = ["default"]
            assert source.check(logger, {"dataset_name": "squad", "api_token": "legacy"}).status == Status.SUCCEEDED
            assert mock_get_configs.call_args.kwargs["token"] == "legacy"

    def test_check_fails_without_a_dataset_name(self, source, logger):
        """Test that an empty dataset name is reported instead of raising."""
        assert source.check(logger, {"dataset_name": ""}).status == Status.FAILED


class TestCheck:
    """Test the check connection method."""

    def test_check_connection_success(self, source, config, logger):
        """Test successful connection check."""
        with patch("datasets.get_dataset_config_names") as mock_get_configs:
            mock_get_configs.return_value = ["default"]
            result = source.check(logger, config)
            assert result.status == Status.SUCCEEDED

    def test_check_connection_failure(self, source, config, logger):
        """Test failed connection check."""
        with patch("datasets.get_dataset_config_names") as mock_get_configs, patch("datasets.load_dataset_builder") as mock_builder:
            mock_get_configs.side_effect = Exception("Dataset not found")
            mock_builder.side_effect = Exception("Dataset not found")
            result = source.check(logger, config)
            assert result.status == Status.FAILED
            assert "Dataset not found" in result.message

    def test_check_succeeds_when_only_the_builder_works(self, source, config, logger):
        """Test that datasets without subsets are still reported as reachable."""
        with patch("datasets.get_dataset_config_names") as mock_get_configs, patch("datasets.load_dataset_builder") as mock_builder:
            mock_get_configs.side_effect = Exception("No configs")
            mock_builder.return_value = object()
            assert source.check(logger, config).status == Status.SUCCEEDED


class TestDiscover:
    """Test the discover method."""

    def test_discover_creates_streams(self, source, config, logger):
        """Test that discover creates streams for each config and split."""
        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset_builder") as mock_builder,
        ):
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train", "test"]
            mock_builder.side_effect = Exception("no schema")

            catalog = source.discover(logger, config)

            assert len(catalog.streams) == 2
            assert [s.name for s in catalog.streams] == ["squad__default__train", "squad__default__test"]

    def test_discover_reads_the_dataset_schema(self, source, config, logger):
        """Test that discovered streams carry the typed schema of the dataset."""
        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset_builder") as mock_builder,
        ):
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train"]
            mock_builder.return_value.info.features = features(
                id=datasets.Value("string"),
                star=datasets.Value("int64"),
                average=datasets.Value("float64"),
                approved=datasets.Value("bool"),
                created=datasets.Value("timestamp[us]"),
                labels=datasets.Sequence(datasets.Value("string")),
                answers={"text": datasets.Value("string")},
                image=datasets.Image(),
            )

            catalog = source.discover(logger, config)

            properties = catalog.streams[0].json_schema["properties"]
            assert properties["id"] == {"type": ["string", "null"]}
            assert properties["star"] == {"type": ["integer", "null"]}
            assert properties["average"] == {"type": ["number", "null"]}
            assert properties["approved"] == {"type": ["boolean", "null"]}
            assert properties["created"] == {"type": ["string", "null"], "format": "date-time"}
            assert properties["labels"] == {"type": ["array", "null"], "items": {"type": ["string", "null"]}}
            assert properties["answers"]["properties"]["text"] == {"type": ["string", "null"]}
            assert properties["image"]["properties"]["bytes"]["type"] == ["string", "null"]
            assert catalog.streams[0].json_schema["additionalProperties"] is True

    def test_discover_is_permissive_when_the_schema_is_unknown(self, source, config, logger):
        """Test that a dataset with unresolvable features is still synced."""
        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset_builder") as mock_builder,
            patch("datasets.load_dataset") as mock_load_dataset,
        ):
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train"]
            mock_builder.return_value.info.features = None
            mock_load_dataset.side_effect = Exception("no schema")

            catalog = source.discover(logger, config)

            assert catalog.streams[0].json_schema["additionalProperties"] is True
            assert "properties" not in catalog.streams[0].json_schema

    def test_discover_filters_subsets_and_splits(self, source, logger):
        """Test that only the configured subsets and splits are discovered."""
        config = {"dataset_name": "squad", "dataset_subsets": ["glue"], "dataset_splits": ["validation"]}
        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset_builder") as mock_builder,
        ):
            mock_get_configs.return_value = ["default", "glue"]
            mock_get_splits.return_value = ["train", "validation"]
            mock_builder.side_effect = Exception("no schema")

            catalog = source.discover(logger, config)

            assert [s.name for s in catalog.streams] == ["squad__glue__validation"]

    def test_discover_skips_unreadable_subsets(self, source, config, logger):
        """Test that one failing subset does not fail the whole discovery."""
        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset_builder") as mock_builder,
        ):

            def list_splits(_path, *_args, config_name=None, **_kwargs):
                if config_name == "broken":
                    raise Exception("bad subset")
                return ["train"]

            mock_get_configs.return_value = ["good", "broken"]
            mock_get_splits.side_effect = list_splits
            mock_builder.side_effect = Exception("no schema")

            catalog = source.discover(logger, config)

            assert [s.name for s in catalog.streams] == ["squad__good__train"]

    def test_discover_fails_on_unknown_dataset(self, source, config, logger):
        """Test that an unreadable dataset is reported as a config error."""
        from airbyte_cdk.utils import AirbyteTracedException

        with patch("datasets.get_dataset_config_names") as mock_get_configs:
            mock_get_configs.side_effect = Exception("401 Client Error")
            with pytest.raises(AirbyteTracedException) as raised:
                source.discover(logger, config)
            assert "401 Client Error" in raised.value.message


class TestRead:
    """Test the read method."""

    def test_read(self, source, config, logger):
        """Test that read returns records from the dataset."""
        mock_dataset = [
            {"id": "1", "context": "Some context"},
            {"id": "2", "context": "Another context"},
        ]

        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset") as mock_load_dataset,
        ):
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train"]
            mock_load_dataset.return_value = mock_dataset

            messages = list(source.read(logger, config, make_catalog("squad__default__train")))
            records = [m for m in messages if m.type == Type.RECORD]
            assert len(records) == 2
            assert records[0].record.data == {"id": "1", "context": "Some context"}
            assert mock_load_dataset.call_args.kwargs["split"] == "train"
            assert mock_load_dataset.call_args.kwargs["streaming"] is False

    def test_read_streaming_config(self, source, logger):
        """Test that the streaming option is forwarded to the datasets library."""
        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset") as mock_load_dataset,
        ):
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train"]
            mock_load_dataset.return_value = [{"id": "1"}]

            list(source.read(logger, {"dataset_name": "squad", "streaming": True}, make_catalog("squad__default__train")))

            assert mock_load_dataset.call_args.kwargs["streaming"] is True

    def test_read_falls_back_on_the_stream_name(self, source, config, logger):
        """Test that a stream missing from discovery is still read by parsing its name."""
        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset") as mock_load_dataset,
        ):
            mock_get_configs.side_effect = Exception("the hub is unreachable")
            mock_get_splits.return_value = ["train"]
            mock_load_dataset.return_value = [{"id": "1"}]

            messages = list(source.read(logger, config, make_catalog("squad__default__train")))

            assert [m for m in messages if m.type == Type.RECORD]
            assert mock_load_dataset.call_args.args[:2] == ("squad", "default")

    def test_read_skips_streams_of_other_datasets(self, source, config, logger):
        """Test that a stale stream name is skipped instead of syncing wrong data."""
        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset") as mock_load_dataset,
        ):
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train"]
            mock_load_dataset.return_value = [{"id": "1"}]

            messages = list(source.read(logger, config, make_catalog("not_a_valid_stream_name")))

            assert not [m for m in messages if m.type == Type.RECORD]
            mock_load_dataset.assert_not_called()

    def test_read_reports_load_failures(self, source, config, logger):
        """Test that a dataset that cannot be loaded does not fail the whole sync."""
        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset") as mock_load_dataset,
        ):
            mock_get_configs.return_value = ["default", "other"]
            mock_get_splits.return_value = ["train"]
            mock_load_dataset.side_effect = Exception("download failed")

            messages = list(source.read(logger, config, make_catalog("squad__default__train")))

            stream_statuses = [m.trace.stream_status.status for m in messages if m.type == Type.TRACE and m.trace and m.trace.stream_status]
            assert AirbyteStreamStatus.INCOMPLETE in stream_statuses

    def test_read_reraises_iteration_failures(self, source, config, logger):
        """Test that a failure in the middle of a stream fails the sync so it can be retried."""
        from airbyte_cdk.utils import AirbyteTracedException

        class FailingDataset:
            def __iter__(self):
                yield {"id": "1"}
                raise ConnectionError("connection reset")

        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset") as mock_load_dataset,
        ):
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train"]
            mock_load_dataset.return_value = FailingDataset()

            with pytest.raises(AirbyteTracedException):
                list(source.read(logger, config, make_catalog("squad__default__train")))

    def test_read_reads_file_columns_as_bytes(self, source, config, logger):
        """Test that image and audio columns are read as file bytes, not as decoded objects."""

        class _Dataset:
            """Stand in for a loaded dataset, with only what a read touches.

            A real dataset with an image column cannot be built here: encoding one needs Pillow,
            which the connector does not depend on.
            """

            def __init__(self, records, features):
                self.records = records
                self.features = features
                self.casts = []

            def cast_column(self, column, feature):
                self.casts.append((column, type(feature).__name__, feature.decode))
                return self

            def __iter__(self):
                return iter(self.records)

        dataset = _Dataset([{"image": {"bytes": b"png-bytes", "path": "a.png"}}], {"image": datasets.Image()})

        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset") as mock_load_dataset,
        ):
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train"]
            mock_load_dataset.return_value = dataset

            messages = list(source.read(logger, config, make_catalog("squad__default__train")))
            record = next(m for m in messages if m.type == Type.RECORD).record.data

            assert dataset.casts == [("image", "Image", False)]
            assert record["image"]["path"] == "a.png"
            assert base64.b64decode(record["image"]["bytes"]) == b"png-bytes"


class TestRecordSerialization:
    """Test that dataset values are converted to JSON serializable values."""

    @pytest.mark.parametrize(
        "value,expected",
        [
            (None, None),
            ("text", "text"),
            (1, 1),
            (1.5, 1.5),
            (True, True),
            (float("nan"), None),
            (float("inf"), None),
            (b"payload", "cGF5bG9hZA=="),
            (np.int64(7), 7),
            (np.float32(0.5), pytest.approx(0.5)),
            (np.array([1, 2]), [1, 2]),
            (Decimal("1.25"), 1.25),
            (datetime(2026, 1, 2, 3, 4, 5), "2026-01-02T03:04:05"),
            ({"a": np.int64(1)}, {"a": 1}),
            ((1, 2), [1, 2]),
            ({1, 2}, [1, 2]),
            (memoryview(b"payload"), "cGF5bG9hZA=="),
        ],
    )
    def test_to_json_safe(self, source, value, expected):
        """Test that every value type a dataset can yield becomes JSON serializable."""
        import orjson

        converted = source._to_json_safe(value)
        assert converted == expected
        orjson.dumps(converted)  # must not raise

    def test_to_json_safe_encodes_decoded_images(self, source):
        """Test that an image which was decoded anyway becomes base64 file bytes."""

        class _PILikeImage:
            """A decoded image column is a PIL image: it has a size and saves itself."""

            size = (2, 2)

            def save(self, buffer, format=None):
                buffer.write(b"png-bytes")

        converted = source._to_json_safe(_PILikeImage())

        assert set(converted) == {"bytes", "path"}
        assert base64.b64decode(converted["bytes"]) == b"png-bytes"
        assert converted["path"] is None

    def test_records_of_a_full_sync_are_json_serializable(self, source, logger):
        """Test that the whole record pipeline survives orjson serialization, as the CDK does."""
        import orjson

        from airbyte_cdk.models import AirbyteMessage, AirbyteMessageSerializer
        from airbyte_cdk.models import Type as MessageType

        dataset = datasets.Dataset.from_dict(
            {
                "text": ["hello", None],
                "count": [1, 2],
                "score": [0.5, None],
                "tags": [["a"], []],
            },
            features=datasets.Features(
                {
                    "text": datasets.Value("string"),
                    "count": datasets.Value("int64"),
                    "score": datasets.Value("float64"),
                    "tags": datasets.Sequence(datasets.Value("string")),
                }
            ),
        )

        with (
            patch("datasets.get_dataset_config_names") as mock_get_configs,
            patch("datasets.get_dataset_split_names") as mock_get_splits,
            patch("datasets.load_dataset") as mock_load_dataset,
        ):
            mock_get_configs.return_value = ["default"]
            mock_get_splits.return_value = ["train"]
            mock_load_dataset.return_value = dataset

            messages = list(source.read(logger, {"dataset_name": "squad"}, make_catalog("squad__default__train")))
            records = [m for m in messages if m.type == Type.RECORD]

            assert len(records) == 2
            for message in records:
                airbyte_message = AirbyteMessage(type=MessageType.RECORD, record=message.record)
                orjson.dumps(AirbyteMessageSerializer.dump(airbyte_message))


class TestStreamNames:
    """Test the stream name handling."""

    def test_parse_stream_name(self):
        """Test that stream names are read back into subsets and splits."""
        assert SourceHuggingFaceDatasets._parse_stream_name("nyu-mll/glue__mrpc__train") == StreamSpec(
            name="nyu-mll/glue__mrpc__train", config_name="mrpc", split_name="train"
        )
        assert SourceHuggingFaceDatasets._parse_stream_name("not_a_stream_name") is None


class TestEntrypoint:
    """Test the connector entry points."""

    def test_main_py_is_wired_to_run(self):
        """Test that `python main.py` can import its run function."""
        main_path = Path(__file__).parent.parent / "main.py"
        spec = importlib.util.spec_from_file_location("connector_main", main_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert callable(module.run)

    def test_run_module_exposes_run(self):
        """Test that the run module is importable, as the Docker image entrypoint expects."""
        from source_hugging_face_datasets import run as run_module

        assert callable(run_module.run)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
