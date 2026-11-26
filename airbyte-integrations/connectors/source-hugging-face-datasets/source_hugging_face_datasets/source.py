#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

"""Hugging Face Datasets source implementation."""

import base64
import io
import logging
import math
import time
import traceback
from datetime import date, datetime, timedelta
from datetime import time as time_type
from decimal import Decimal
from typing import Any, Dict, Iterator, List, Mapping, MutableMapping, NamedTuple, Optional

import datasets

from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    ConfiguredAirbyteCatalog,
    ConnectorSpecification,
    DestinationSyncMode,
    FailureType,
    Status,
    SyncMode,
    Type,
)
from airbyte_cdk.sources import Source
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_cdk.utils.stream_status_utils import (
    as_airbyte_message as stream_status_as_airbyte_message,
)


# Separator used to build the `{dataset}__{config}__{split}` stream names.
STREAM_SEPARATOR = "__"

# 0.1.0 renamed this field to `token`. Existing connections still carry it, so it is read
# as a fallback and documented as deprecated.
LEGACY_TOKEN_FIELD = "api_token"

# Feature types holding file payloads. They are read with `decode=False` so that the
# connector does not need the optional image/audio decoding dependencies, and so records
# carry the original file bytes instead of a decoded object.
ENCODED_FEATURE_CLASS_NAMES = {"Image", "Audio", "Video"}


class StreamSpec(NamedTuple):
    """A single readable slice of a dataset: one subset and one split."""

    name: str
    config_name: str
    split_name: str


class SourceHuggingFaceDatasets(Source):
    """Source reading datasets from the Hugging Face Hub with the `datasets` library."""

    def spec(self, logger: logging.Logger) -> ConnectorSpecification:
        """Returns the connector specification."""
        return ConnectorSpecification(
            connectionSpecification={
                "$schema": "http://json-schema.org/draft-07/schema#",
                "title": "Source Hugging Face Datasets",
                "type": "object",
                "required": ["dataset_name"],
                "additionalProperties": True,
                "properties": {
                    "dataset_name": {
                        "order": 0,
                        "title": "Dataset name",
                        "type": "string",
                        "description": "The dataset identifier on the Hugging Face Hub, for example 'nyu-mll/glue'. See the dataset page URL at https://huggingface.co/datasets.",
                    },
                    "dataset_subsets": {
                        "order": 1,
                        "title": "Dataset subsets",
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [],
                        "description": "Subsets (configs) to sync. All of them are synced if nothing is provided. See https://huggingface.co/docs/dataset-viewer/en/configs_and_splits#configs.",
                    },
                    "dataset_splits": {
                        "order": 2,
                        "title": "Dataset splits",
                        "type": "array",
                        "items": {"type": "string"},
                        "default": [],
                        "description": "Splits to sync, for example 'train'. All of them are synced if nothing is provided. See https://huggingface.co/docs/dataset-viewer/en/configs_and_splits#splits.",
                    },
                    "token": {
                        "order": 3,
                        "title": "Hugging Face token",
                        "type": "string",
                        "airbyte_secret": True,
                        "description": "Hugging Face token, used to read private or gated datasets and to raise the anonymous rate limits. Optional for public datasets. Create one at https://huggingface.co/settings/tokens.",
                    },
                    "streaming": {
                        "order": 4,
                        "title": "Streaming mode",
                        "type": "boolean",
                        "default": False,
                        "description": "When enabled, records are read from the Hub on the fly instead of being downloaded and cached to disk. Slower, but it handles datasets larger than the available disk. See https://huggingface.co/docs/datasets/stream.",
                    },
                    "api_token": {
                        "order": 5,
                        "title": "Hugging Face API token (deprecated)",
                        "type": "string",
                        "airbyte_secret": True,
                        "description": "Deprecated: replaced by the 'Hugging Face token' field. Connections configured before 0.1.0 keep working through this field.",
                    },
                },
            },
            documentationUrl="https://docs.airbyte.com/integrations/sources/hugging-face-datasets",
            supportsIncremental=False,
            supported_destination_sync_modes=[DestinationSyncMode.append, DestinationSyncMode.overwrite],
        )

    @staticmethod
    def _get_token(config: Mapping[str, Any]) -> Optional[str]:
        """Read the token, falling back on the pre-0.1.0 `api_token` field."""
        return config.get("token") or config.get(LEGACY_TOKEN_FIELD) or None

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """Test the connection by listing the dataset subsets, which downloads no data."""
        dataset_name = config.get("dataset_name", "")
        if not dataset_name:
            return AirbyteConnectionStatus(status=Status.FAILED, message="The `dataset_name` field is required.")

        token = self._get_token(config)
        last_error: Optional[Exception] = None
        for probe in (
            lambda: datasets.get_dataset_config_names(dataset_name, token=token),
            lambda: datasets.load_dataset_builder(dataset_name, token=token),
        ):
            try:
                probe()
                logger.info(f"Connection check successful for dataset: {dataset_name}")
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            except Exception as err:  # the last error is reported back to the user
                last_error = err

        reason = f"Connection check failed for dataset {dataset_name}: {last_error}"
        logger.error(f"{reason}\n{traceback.format_exc()}")
        return AirbyteConnectionStatus(status=Status.FAILED, message=reason)

    def _iter_stream_specs(self, config: Mapping[str, Any], logger: logging.Logger) -> Iterator[StreamSpec]:
        """Yield one StreamSpec per (subset, split) pair to sync.

        Both `discover` and `read` use this method, so stream names never need to be parsed
        back into their parts.
        """
        dataset_name = config.get("dataset_name", "")
        token = self._get_token(config)
        requested_subsets = config.get("dataset_subsets") or []
        requested_splits = config.get("dataset_splits") or []

        all_subsets = datasets.get_dataset_config_names(dataset_name, token=token)
        subsets = [subset for subset in requested_subsets if subset in all_subsets] if requested_subsets else all_subsets
        if requested_subsets and not subsets:
            logger.warning(f"None of the configured subsets {requested_subsets} exist in {dataset_name}: syncing all of them instead.")
            subsets = all_subsets

        for config_name in subsets:
            try:
                all_splits = datasets.get_dataset_split_names(dataset_name, config_name=config_name, token=token)
            except Exception as err:  # an unreadable subset should not fail the whole sync
                logger.warning(f"Failed to list the splits of {dataset_name}/{config_name}: {err}")
                continue

            splits = [split for split in requested_splits if split in all_splits] if requested_splits else all_splits
            if requested_splits and not splits:
                logger.warning(
                    f"None of the configured splits {requested_splits} exist in {dataset_name}/{config_name}: using all of them."
                )
                splits = all_splits

            for split_name in splits:
                yield StreamSpec(
                    name=f"{dataset_name}{STREAM_SEPARATOR}{config_name}{STREAM_SEPARATOR}{split_name}",
                    config_name=config_name,
                    split_name=split_name,
                )

    def _get_features(
        self,
        dataset_name: str,
        config_name: str,
        split_name: str,
        token: Optional[str],
        logger: logging.Logger,
    ) -> Optional[Dict[str, Any]]:
        """Read the dataset features (its typed columns) without downloading any row."""
        try:
            builder = datasets.load_dataset_builder(dataset_name, name=config_name, token=token)
            if builder.info.features:
                return builder.info.features
        except Exception as err:  # the schema is best effort, a permissive one is used otherwise
            logger.debug(f"Could not read the features of {dataset_name}/{config_name} from the builder: {err}")

        try:
            # Some datasets only resolve their features once a split is prepared, which
            # preparing a streaming split does without downloading the data itself.
            dataset = datasets.load_dataset(dataset_name, config_name, split=split_name, token=token, streaming=True)
            features = getattr(dataset, "features", None)
            if features:
                return features
        except Exception as err:  # the schema is best effort, a permissive one is used otherwise
            logger.debug(f"Could not read the features of {dataset_name}/{config_name} from a streaming load: {err}")

        return None

    def _schema_from_features(self, features: Optional[Mapping[str, Any]]) -> dict:
        """Convert dataset features into a JSON schema, or into a permissive schema if unknown."""
        if not features:
            return {"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "additionalProperties": True}

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {column: self._json_type(feature) for column, feature in features.items()},
            "additionalProperties": True,
        }

    def _json_type(self, feature: Any) -> dict:
        """Map a single `datasets` feature to a JSON schema type."""
        class_name = type(feature).__name__

        # File columns are synced as `{"bytes": ..., "path": ...}` objects, bytes being base64 encoded.
        if class_name in ENCODED_FEATURE_CLASS_NAMES:
            return {
                "type": ["object", "null"],
                "properties": {
                    "bytes": {"type": ["string", "null"], "description": "Base64 encoded file content."},
                    "path": {"type": ["string", "null"]},
                },
                "additionalProperties": True,
            }

        # ClassLabel exposes integer labels.
        if class_name == "ClassLabel":
            return {"type": ["integer", "null"]}

        # Sequence, List and LargeList wrap a single inner feature.
        if hasattr(feature, "feature"):
            return {"type": ["array", "null"], "items": self._json_type(feature.feature)}

        # Translation and TranslationVariableLanguages wrap a list of features.
        inner_features = getattr(feature, "features", None)
        if isinstance(inner_features, (list, tuple)) and inner_features:
            inner_types = [self._json_type(inner) for inner in inner_features]
            return {"type": ["array", "null"], "items": inner_types[0] if len(inner_types) == 1 else {"oneOf": inner_types}}

        # A dict feature is an object with one property per key.
        if isinstance(feature, dict):
            return {
                "type": ["object", "null"],
                "properties": {key: self._json_type(value) for key, value in feature.items()},
                "additionalProperties": True,
            }

        # Value and its subclasses expose an Arrow dtype such as `string` or `int64`.
        dtype = str(getattr(feature, "dtype", "")).lower()
        if dtype.startswith(("timestamp", "date", "time")):
            return {"type": ["string", "null"], "format": "date-time"}
        if dtype.startswith(("binary", "large_binary")):
            return {"type": ["string", "null"], "description": "Base64 encoded content."}
        if dtype.startswith(("int", "uint")):
            return {"type": ["integer", "null"]}
        if dtype.startswith(("float", "double", "decimal")):
            return {"type": ["number", "null"]}
        if dtype.startswith("bool"):
            return {"type": ["boolean", "null"]}
        if dtype.startswith(("string", "large_string", "utf8", "char")):
            return {"type": ["string", "null"]}

        # Unknown feature type: accept any value rather than dropping the column.
        return {}

    def _to_json_safe(self, value: Any) -> Any:
        """Convert a dataset value into something the Airbyte protocol can serialize as JSON."""
        if value is None or isinstance(value, (bool, int, str)):
            return value
        if isinstance(value, float):
            # NaN and infinities have no JSON representation, sync them as missing values.
            return value if math.isfinite(value) else None
        if isinstance(value, (bytes, bytearray, memoryview)):
            return base64.b64encode(bytes(value)).decode("ascii")
        if isinstance(value, Mapping):
            return {str(key): self._to_json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._to_json_safe(item) for item in value]
        if isinstance(value, (datetime, date, time_type, timedelta)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if hasattr(value, "tolist"):  # numpy arrays and scalars
            return self._to_json_safe(value.tolist())
        if hasattr(value, "save") and hasattr(value, "size"):  # PIL images that were not read as bytes
            buffer = io.BytesIO()
            value.save(buffer, format=getattr(value, "format", None) or "PNG")
            return {"bytes": base64.b64encode(buffer.getvalue()).decode("ascii"), "path": getattr(value, "filename", None)}
        # Any other custom object: keep its string form rather than failing the whole sync.
        return str(value)

    def _raw_file_columns(self, dataset: Any, features: Optional[Mapping[str, Any]], logger: logging.Logger) -> Any:
        """Read image, audio and video columns as file bytes rather than decoded objects.

        Decoding those columns needs optional dependencies (`Pillow`, `torchcodec`) and yields
        objects the protocol cannot serialize, so they are switched to `decode=False`.
        """
        for column, feature in (features or {}).items():
            if type(feature).__name__ not in ENCODED_FEATURE_CLASS_NAMES or not getattr(feature, "decode", False):
                continue
            try:
                dataset = dataset.cast_column(column, type(feature)(decode=False))
            except Exception as err:  # the column is still readable, only its shape changes
                logger.warning(f"Could not read column {column} as file bytes: {err}")
        return dataset

    def discover(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteCatalog:
        """Discover one stream per dataset subset and split, with the dataset schema."""
        dataset_name = config.get("dataset_name", "")
        if not dataset_name:
            raise AirbyteTracedException(
                message="The `dataset_name` field is required",
                internal_message="The `dataset_name` field is required",
                failure_type=FailureType.config_error,
            )

        token = self._get_token(config)
        try:
            specs = list(self._iter_stream_specs(config, logger))
        except Exception as err:  # re-raised as a config error for the platform
            reason = f"Failed to discover the dataset {dataset_name}: {err}"
            logger.error(f"{reason}\n{traceback.format_exc()}")
            raise AirbyteTracedException(message=reason, internal_message=str(err), failure_type=FailureType.config_error)

        streams: List[AirbyteStream] = []
        schemas: Dict[str, dict] = {}
        for spec in specs:
            if spec.config_name not in schemas:
                features = self._get_features(dataset_name, spec.config_name, spec.split_name, token, logger)
                schemas[spec.config_name] = self._schema_from_features(features)
            streams.append(
                AirbyteStream(
                    name=spec.name,
                    json_schema=schemas[spec.config_name],
                    supported_sync_modes=[SyncMode.full_refresh],
                )
            )

        logger.info(f"Discovered {len(streams)} streams from dataset {dataset_name}")
        return AirbyteCatalog(streams=streams)

    def read(
        self,
        logger: logging.Logger,
        config: Mapping[str, Any],
        catalog: ConfiguredAirbyteCatalog,
        state: Optional[MutableMapping[str, Any]] = None,
    ) -> Iterator[AirbyteMessage]:
        """Read each configured stream with the `datasets` library."""
        dataset_name = config.get("dataset_name", "")
        token = self._get_token(config)
        streaming = bool(config.get("streaming", False))

        # Maps the stream names of this dataset back to their subset and split. It is built on
        # first use so that a sync of an already configured catalog does not need discovery.
        specs_by_name: Optional[Dict[str, StreamSpec]] = None

        for configured_stream in catalog.streams:
            airbyte_stream = configured_stream.stream
            stream_name = airbyte_stream.name

            if specs_by_name is None:
                try:
                    specs_by_name = {spec.name: spec for spec in self._iter_stream_specs(config, logger)}
                except Exception as err:  # discovery is only a lookup helper here
                    logger.warning(f"Could not list the streams of {dataset_name}, falling back on the stream names: {err}")
                    specs_by_name = {}

            spec = specs_by_name.get(stream_name) or self._parse_stream_name(stream_name)
            if spec is None:
                logger.warning(f"Stream {stream_name} does not match any subset and split of {dataset_name}: skipping")
                continue

            yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.STARTED)
            logger.info(f"Syncing stream {stream_name} (subset={spec.config_name}, split={spec.split_name}, streaming={streaming})")

            try:
                dataset = datasets.load_dataset(
                    dataset_name,
                    spec.config_name,
                    split=spec.split_name,
                    token=token,
                    streaming=streaming,
                )
                dataset = self._raw_file_columns(dataset, getattr(dataset, "features", None), logger)
            except Exception as err:  # an unreadable stream should not fail the other streams
                logger.error(f"Failed to load {dataset_name}/{spec.config_name}/{spec.split_name}: {err}\n{traceback.format_exc()}")
                yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.INCOMPLETE)
                continue

            record_count = 0
            try:
                for record in dataset:
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(
                            stream=stream_name,
                            data=self._to_json_safe(record),
                            emitted_at=int(time.time() * 1000),
                        ),
                    )
                    record_count += 1
                    if record_count == 1:
                        yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.RUNNING)
            except Exception as err:  # re-raised so the platform can retry the sync
                logger.error(f"Failed to read {stream_name}: {err}\n{traceback.format_exc()}")
                yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.INCOMPLETE)
                raise AirbyteTracedException(
                    message=f"Failed to read {stream_name}: {err}",
                    internal_message=str(err),
                    failure_type=FailureType.transient_error,
                )

            logger.info(f"Successfully read {record_count} records from {stream_name}")
            yield stream_status_as_airbyte_message(airbyte_stream, AirbyteStreamStatus.COMPLETE)

    @staticmethod
    def _parse_stream_name(stream_name: str) -> Optional[StreamSpec]:
        """Recover the subset and split of a stream name, used when discovery is unavailable.

        Hub dataset identifiers cannot contain `_`, so `{dataset}__{subset}__{split}` normally
        splits into exactly three parts.
        """
        parts = stream_name.split(STREAM_SEPARATOR)
        if len(parts) < 3:
            return None
        return StreamSpec(name=stream_name, config_name=parts[1], split_name=parts[-1])
