#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.sources.declarative.models import (
    CustomRetriever,
    DatetimeBasedCursor,
    DeclarativeStream,
    ParentStreamConfig,
    SubstreamPartitionRouter,
)
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from source_klaviyo.components.per_partition_state_migration import PerPartitionToSingleStateMigration

factory = ModelToComponentFactory()

resolver = ManifestReferenceResolver()

transformer = ManifestComponentTransformer()


def test_migrate_a_valid_legacy_state_to_per_partition():
    input_state = {
        "states": [
            {
                "partition": {"parent_id": "13506132"},
                "cursor": {"last_changed": "2023-12-27T08:34:39+00:00"}
            },
            {
                "partition": {"parent_id": "14351124"},
                "cursor": {"last_changed": "2022-12-27T08:35:39+00:00"}
            },
        ]
    }

    migrator = _migrator()

    assert migrator.should_migrate(input_state)

    expected_state = {"last_changed": "2022-12-27T08:35:39+00:00"}

    assert migrator.migrate(input_state) == expected_state


def test_should_not_migrate():
    input_state = {"last_changed": "2022-12-27T08:35:39+00:00"}
    migrator = _migrator()
    assert not migrator.should_migrate(input_state)


def _migrator():
    partition_router = SubstreamPartitionRouter(
        type="SubstreamPartitionRouter",
        parent_stream_configs=[
            ParentStreamConfig(
                type="ParentStreamConfig",
                parent_key="{{ parameters['parent_key_id'] }}",
                partition_field="parent_id",
                stream=DeclarativeStream(
                    type="DeclarativeStream",
                    retriever=CustomRetriever(
                        type="CustomRetriever",
                        class_name="a_class_name"
                    )
                )
            )
        ]
    )
    cursor = DatetimeBasedCursor(
        type="DatetimeBasedCursor",
        cursor_field="{{ parameters['cursor_field'] }}",
        datetime_format="%Y-%m-%dT%H:%M:%S.%fZ",
        start_datetime="1970-01-01T00:00:00.0Z",
    )
    config = {}
    parameters = {"cursor_field": "last_changed", "parent_key_id": "id"}

    declarative_stream = MagicMock()
    declarative_stream.retriever.partition_router = partition_router
    declarative_stream.incremental_sync = cursor
    declarative_stream.parameters = parameters

    return PerPartitionToSingleStateMigration(config=config, declarative_stream=declarative_stream)
