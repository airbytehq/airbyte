#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

"""Hugging Face Datasets Source implementation."""

import json
import logging
import time
import traceback
from typing import Any, Iterator, Mapping, MutableMapping

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    FailureType,
    Status,
    Type,
)
from airbyte_cdk.sources import Source
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.stream_status_utils import (
    as_airbyte_message as stream_status_as_airbyte_message,
)


class SourceHuggingFaceDatasets(Source):
    """Source for reading data from Hugging Face Datasets using the datasets library."""

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        """Returns the connector specification."""
        return ConnectorSpecification(
            connectionSpecification={
                "title": "Dataset Configuration",
                "properties": {
                    "dataset_name": {
                        "order": 0,
                        "title": "Dataset Name",
                        "type": "string",
                        "description": "The name of the dataset on Hugging Face (e.g., 'glue', 'squad', 'imdb')",
                    },
                    "dataset_subsets": {
                        "order": 1,
                        "title": "Dataset Subsets/Configurations",
                        "type": "array",
                        "description": "List of dataset subsets (configs) to import. If empty, all subsets will be imported.",
                        "items": {"type": "string"},
                    },
                    "dataset_splits": {
                        "order": 2,
                        "title": "Dataset Splits",
                        "type": "array",
                        "description": "List of dataset splits to import. If empty, all splits will be imported. Common values: 'train', 'test', 'validation'.",
                        "items": {"type": "string"},
                    },
                    "token": {
                        "order": 3,
                        "title": "HF Token (Optional)",
                        "type": "string",
                        "description": "Hugging Face token for private datasets.",
                    },
                    "streaming": {
                        "order": 4,
                        "title": "Streaming Mode",
                        "type": "boolean",
                        "default": False,
                        "description": "When true, datasets are streamed on-the-fly without caching to disk. Use this for very large datasets where you don't want to fill disk space. Note: streaming mode is slower and less reliable than non-streaming mode.",
                    },
                },
                "required": ["dataset_name"],
                "type": "object",
            },
            documentationUrl="https://docs.airbyte.com/integrations/sources/hugging-face-datasets",
            supports_incremental=False,
            supported_destination_sync_modes=["append", "overwrite"],
        )

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Check connection by attempting to list dataset configs."""
        try:
            import datasets

            dataset_name = config.get("dataset_name", "")
            token = config.get("token", None)

            # Use get_dataset_config_names to verify access without downloading data
            config_names = datasets.get_dataset_config_names(dataset_name, token=token)
            logger.info(f"Connection check successful for dataset: {dataset_name} ({len(config_names)} configs)")

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        except Exception as err:
            reason = f"Connection check failed: {str(err)}"
            logger.error(f"{reason}\n{traceback.format_exc()}")
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=reason,
            )

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Discover available streams from the dataset."""
        import datasets

        dataset_name = config.get("dataset_name", "")
        token = config.get("token", None)
        dataset_subsets = config.get("dataset_subsets", [])
        dataset_splits = config.get("dataset_splits", [])

        streams = []

        try:
            # Get available configs (subsets) without downloading data
            all_configs = datasets.get_dataset_config_names(dataset_name, token=token)

            # Filter configs if specified
            if dataset_subsets:
                configs_to_load = [c for c in dataset_subsets if c in all_configs]
                if not configs_to_load:
                    configs_to_load = all_configs
            else:
                configs_to_load = all_configs

            # For each config, discover splits and create streams
            for config_name in configs_to_load:
                try:
                    # Get available splits for this config
                    all_splits = datasets.get_dataset_split_names(dataset_name, config_name=config_name, token=token)

                    # Filter splits if specified
                    if dataset_splits:
                        splits_to_load = [s for s in dataset_splits if s in all_splits]
                        if not splits_to_load:
                            splits_to_load = all_splits
                    else:
                        splits_to_load = all_splits

                    for split_name in splits_to_load:
                        # Create stream name: dataset_name__config__split
                        stream_name = f"{dataset_name}__{config_name}__{split_name}"

                        # Use a dynamic schema - actual schema discovered during read
                        streams.append(
                            AirbyteStream(
                                name=stream_name,
                                json_schema={"type": "object", "additionalProperties": True},
                                supported_sync_modes=["full_refresh"],
                            )
                        )

                except Exception as inner_err:
                    logger.warning(f"Failed to discover config {config_name}: {str(inner_err)}")

            logger.info(f"Discovered {len(streams)} streams from dataset {dataset_name}")

        except Exception as err:
            reason = f"Failed to discover dataset: {str(err)}"
            logger.error(f"{reason}\n{traceback.format_exc()}")
            raise AirbyteTracedException(
                message=reason,
                internal_message=reason,
                failure_type=FailureType.config_error,
            )

        return AirbyteCatalog(streams=streams)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: MutableMapping[str, Any] = None,
    ) -> Iterator[AirbyteMessage]:
        """Read data from Hugging Face datasets using the datasets library."""
        import datasets

        dataset_name = config.get("dataset_name", "")
        token = config.get("token", None)

        logger.info(f"Starting read for dataset: {dataset_name}")

        try:
            for configured_stream in catalog.streams:
                airbyte_stream = configured_stream.stream
                stream_name = airbyte_stream.name

                # Parse the stream name to get config and split
                # Format: dataset_name__config_name__split_name
                parts = stream_name.split("__")
                if len(parts) < 3:
                    logger.warning(f"Invalid stream name format: {stream_name}, skipping")
                    continue

                config_name = parts[1]
                split_name = parts[2]

                yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.STARTED)

                logger.info(f"Syncing stream: {stream_name} (config={config_name}, split={split_name})")

                # Load the dataset using the datasets library
                try:
                    streaming = config.get("streaming", False)
                    logger.info(f"Loading dataset {dataset_name} config={config_name} split={split_name} (streaming={streaming})")
                    dataset = datasets.load_dataset(
                        dataset_name,
                        config_name,
                        split=split_name,
                        token=token,
                        streaming=streaming,
                    )
                    # In streaming mode, wrap in list to get an indexable dataset
                    # (streaming returns IterableDataset which can't be len() or indexed,
                    # but iterating works the same)
                    if streaming:
                        logger.info("Using streaming mode - iterating directly from source")
                except Exception as load_err:
                    logger.error(f"Failed to load dataset {dataset_name} config={config_name} split={split_name}: {load_err}")
                    yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.INCOMPLETE)
                    continue

                # Read records
                record_count = 0
                try:
                    for record in dataset:
                        yield AirbyteMessage(
                            type=Type.RECORD,
                            record=AirbyteRecordMessage(
                                stream=stream_name,
                                data=record,
                                emitted_at=int(time.time() * 1000),
                            ),
                        )
                        record_count += 1

                        if record_count == 1:
                            logger.info(f"Marking stream {stream_name} as RUNNING")
                            yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.RUNNING)

                    logger.info(f"Successfully read {record_count} records from {stream_name}")

                except Exception as read_err:
                    logger.error(f"Failed to read data from {stream_name}: {str(read_err)}\n{traceback.format_exc()}")
                    yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.INCOMPLETE)
                    raise AirbyteTracedException(
                        message=f"Failed to read {stream_name}: {str(read_err)}",
                        internal_message=str(read_err),
                        failure_type=FailureType.retriable_error,
                    )

                yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.COMPLETE)

        except Exception as err:
            logger.error(f"Read failed: {str(err)}\n{traceback.format_exc()}")
            raise
