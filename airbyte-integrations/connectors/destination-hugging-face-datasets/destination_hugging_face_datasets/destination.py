#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

import logging
import uuid
from typing import Any, Iterable, Mapping, Optional

import pandas as pd
from datasets import Dataset
from huggingface_hub import HfApi

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import (
    AirbyteConnectionStatus,
    AirbyteMessage,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)


class DestinationHuggingFaceDatasets(Destination):
    """A destination that writes data to Hugging Face Datasets.

    This destination writes data to Hugging Face Datasets using the `datasets` library's
    `push_to_hub()` functionality. Records are collected and written as Parquet files
    to the specified dataset on Hugging Face Hub.
    """

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """Write data to Hugging Face Datasets.

        Args:
            config: Configuration dictionary for the destination.
            configured_catalog: The catalog describing how to write data.
            input_messages: Stream of Airbyte messages containing records.

        Returns:
            Iterable of Airbyte messages, including state messages.
        """
        dataset_name = config.get("dataset_name", "")
        token = config.get("token", None)

        if not dataset_name:
            raise ValueError("dataset_name is required")

        if not token:
            raise ValueError("token is required")

        # Buffer records for each stream
        stream_buffers: dict = {}

        try:
            for message in input_messages:
                if message.type == Type.STATE:
                    # Emit state messages as-is
                    yield message
                elif message.type == Type.RECORD:
                    if message.record is None:
                        continue

                    stream_name = message.record.stream or "default"
                    record_data = message.record.data or {}

                    if stream_name not in stream_buffers:
                        stream_buffers[stream_name] = []

                    stream_buffers[stream_name].append(record_data)

                elif message.type == Type.TRACE:
                    # Forward trace messages
                    yield message
                else:
                    # Ignore other message types
                    continue

            # Write all buffered data to Hugging Face Datasets
            for stream_name, records in stream_buffers.items():
                if records:
                    self._push_to_hub(dataset_name, stream_name, self._dataset_from_records(records), token)

        except Exception as e:
            logging.error(f"Write failed: {str(e)}")
            raise

    @staticmethod
    def _dataset_from_records(records: list) -> Dataset:
        """Build a dataset from records, keeping nested values as they are.

        `datasets` infers the schema from the records directly. The pandas round trip is only used
        as a fallback because it turns nested values into Python objects Arrow rejects.
        """
        try:
            return Dataset.from_list(records)
        except Exception as error:
            logging.warning(f"Could not infer a schema from the records, falling back on pandas: {error}")
            return Dataset.from_pandas(pd.DataFrame(records))

    def _push_to_hub(self, dataset_name: str, stream_name: str, dataset: Dataset, token: Optional[str]):
        """Push data to Hugging Face Hub as a dataset.

        Args:
            dataset_name: Base dataset name.
            stream_name: Stream name to use as subset.
            dataset: The records to push.
            token: Hugging Face token.
        """
        try:
            # Push to HF Hub - writes Parquet files under the hood
            dataset.push_to_hub(dataset_name, stream_name, token=token)
            logging.info(f"Successfully pushed {len(dataset)} records of {stream_name} to {dataset_name}")

        except Exception as e:
            logging.error(f"Failed to push {stream_name} to Hub: {str(e)}")
            raise

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Test the connection by checking if we can create and push to HF Datasets.

        Args:
            logger: Logger for the connector.
            config: The configuration dictionary.

        Returns:
            AirbyteConnectionStatus indicating success or failure.
        """
        try:
            dataset_name = config.get("dataset_name", "")
            token = config.get("token", None)

            if not dataset_name:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message="dataset_name is required",
                )

            # If we can create a branch then we can write to the dataset
            branch = f"_airbyte_check_{uuid.uuid4().hex}"
            api = HfApi(token=token)
            try:
                api.create_branch(dataset_name, branch=branch, repo_type="dataset")
                api.delete_branch(dataset_name, branch=branch, repo_type="dataset")
            except Exception as branch_error:
                # The dataset is created by the first sync, so a dataset that does not exist yet
                # is a valid configuration as long as it can be created with this token.
                try:
                    api.create_repo(dataset_name, repo_type="dataset", exist_ok=True)
                except Exception:
                    raise branch_error

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED,
                message=f"Connection check failed: {str(e)}",
            )
