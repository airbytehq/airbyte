#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.sources.declarative.migrations.legacy_to_per_partition_state_migration import LegacyToPerPartitionStateMigration
from airbyte_cdk.sources.declarative.models import CustomPartitionRouter, CustomRetriever, DatetimeBasedCursor, DeclarativeStream
from airbyte_cdk.sources.declarative.models import LegacyToPerPartitionStateMigration as LegacyToPerPartitionStateMigrationModel
from airbyte_cdk.sources.declarative.models import ParentStreamConfig, SimpleRetriever, SubstreamPartitionRouter
from airbyte_cdk.sources.declarative.parsers.manifest_component_transformer import ManifestComponentTransformer
from airbyte_cdk.sources.declarative.parsers.manifest_reference_resolver import ManifestReferenceResolver
from airbyte_cdk.sources.declarative.parsers.model_to_component_factory import ModelToComponentFactory
from airbyte_cdk.sources.declarative.yaml_declarative_source import YamlDeclarativeSource

factory = ModelToComponentFactory()

resolver = ManifestReferenceResolver()

transformer = ManifestComponentTransformer()


def test_migrate_a_valid_legacy_state_to_per_partition():
    input_state = {
        "13506132": {"last_changed": "2022-12-27T08:34:39+00:00"},
        "14351124": {"last_changed": "2022-12-27T08:35:39+00:00"},
    }

    migrator = _migrator()

    assert migrator.should_migrate(input_state)

    expected_state = {
        "states": [
            {"partition": {"parent_id": "13506132"}, "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
            {"partition": {"parent_id": "14351124"}, "cursor": {"last_changed": "2022-12-27T08:35:39+00:00"}},
        ]
    }

    assert migrator.migrate(input_state) == expected_state


@pytest.mark.parametrize(
    "input_state",
    [
        pytest.param(
            {
                "states": [
                    {"partition": {"id": "13506132"}, "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
                    {"partition": {"id": "14351124"}, "cursor": {"last_changed": "2022-12-27T08:35:39+00:00"}},
                ]
            },
            id="test_should_not_migrate_a_per_partition_state",
        ),
        pytest.param(
            {
                "states": [
                    {"partition": {"id": "13506132"}, "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
                    {
                        "partition": {"id": "14351124"},
                    },
                ]
            },
            id="test_should_not_migrate_state_without_a_cursor_component",
        ),
        pytest.param(
            {
                "states": [
                    {"partition": {"id": "13506132"}, "cursor": {"updated_at": "2022-12-27T08:34:39+00:00"}},
                    {"partition": {"id": "14351124"}, "cursor": {"updated_at": "2022-12-27T08:35:39+00:00"}},
                ]
            },
            id="test_should_not_migrate_a_per_partition_state_with_wrong_cursor_field",
        ),
        pytest.param(
            {
                "states": [
                    {"partition": {"id": "13506132"}, "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
                    {"partition": {"id": "14351124"}, "cursor": {"last_changed": "2022-12-27T08:35:39+00:00", "updated_at": "2021-01-01"}},
                ]
            },
            id="test_should_not_migrate_a_per_partition_state_with_multiple_cursor_fields",
        ),
        pytest.param(
            {
                "states": [
                    {"partition": {"id": "13506132"}, "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
                    {"cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
                ]
            },
            id="test_should_not_migrate_state_without_a_partition_component",
        ),
        pytest.param(
            {
                "states": [
                    {"partition": {"id": "13506132", "another_id": "A"}, "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
                    {"partition": {"id": "13506134"}, "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
                ]
            },
            id="test_should_not_migrate_state_if_multiple_partition_keys",
        ),
        pytest.param(
            {
                "states": [
                    {"partition": {"identifier": "13506132"}, "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
                    {"partition": {"id": "13506134"}, "cursor": {"last_changed": "2022-12-27T08:34:39+00:00"}},
                ]
            },
            id="test_should_not_migrate_state_if_invalid_partition_key",
        ),
        pytest.param(
            {
                "13506132": {"last_changed": "2022-12-27T08:34:39+00:00"},
                "14351124": {"last_changed": "2022-12-27T08:35:39+00:00", "another_key": "2022-12-27T08:35:39+00:00"},
            },
            id="test_should_not_migrate_if_the_partitioned_state_has_more_than_one_key",
        ),
        pytest.param(
            {
                "13506132": {"last_changed": "2022-12-27T08:34:39+00:00"},
                "14351124": {"another_key": "2022-12-27T08:35:39+00:00"},
            },
            id="test_should_not_migrate_if_the_partitioned_state_key_is_not_the_cursor_field",
        ),
    ],
)
def test_should_not_migrate(input_state):
    migrator = _migrator()
    assert not migrator.should_migrate(input_state)


def test_should_not_migrate_stream_with_multiple_parent_streams():
    input_state = {
        "13506132": {"last_changed": "2022-12-27T08:34:39+00:00"},
        "14351124": {"last_changed": "2022-12-27T08:35:39+00:00"},
    }

    migrator = _migrator_with_multiple_parent_streams()

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
                    type="DeclarativeStream", retriever=CustomRetriever(type="CustomRetriever", class_name="a_class_name")
                ),
            )
        ],
    )
    cursor = DatetimeBasedCursor(
        type="DatetimeBasedCursor",
        cursor_field="{{ parameters['cursor_field'] }}",
        datetime_format="%Y-%m-%dT%H:%M:%S.%fZ",
        start_datetime="1970-01-01T00:00:00.0Z",
    )
    config = {}
    parameters = {"cursor_field": "last_changed", "parent_key_id": "id"}
    return LegacyToPerPartitionStateMigration(partition_router, cursor, config, parameters)


def _migrator_with_multiple_parent_streams():
    partition_router = SubstreamPartitionRouter(
        type="SubstreamPartitionRouter",
        parent_stream_configs=[
            ParentStreamConfig(
                type="ParentStreamConfig",
                parent_key="id",
                partition_field="parent_id",
                stream=DeclarativeStream(
                    type="DeclarativeStream", retriever=CustomRetriever(type="CustomRetriever", class_name="a_class_name")
                ),
            ),
            ParentStreamConfig(
                type="ParentStreamConfig",
                parent_key="id",
                partition_field="parent_id",
                stream=DeclarativeStream(
                    type="DeclarativeStream", retriever=CustomRetriever(type="CustomRetriever", class_name="a_class_name")
                ),
            ),
        ],
    )
    cursor = DatetimeBasedCursor(
        type="DatetimeBasedCursor",
        cursor_field="{{ parameters['cursor_field'] }}",
        datetime_format="%Y-%m-%dT%H:%M:%S.%fZ",
        start_datetime="1970-01-01T00:00:00.0Z",
    )
    config = {}
    parameters = {}
    return LegacyToPerPartitionStateMigration(partition_router, cursor, config, parameters)


@pytest.mark.parametrize(
    "retriever_type, partition_router_class, is_parent_stream_config, expected_exception, expected_error_message",
    [
        (SimpleRetriever, CustomPartitionRouter, True, None, None),
        (
            None,
            CustomPartitionRouter,
            True,
            ValueError,
            "LegacyToPerPartitionStateMigrations can only be applied on a DeclarativeStream with a SimpleRetriever. Got <class 'unittest.mock.MagicMock'>",
        ),
        (
            SimpleRetriever,
            None,
            False,
            ValueError,
            "LegacyToPerPartitionStateMigrations can only be applied on a SimpleRetriever with a Substream partition router. Got <class 'NoneType'>",
        ),
        (
            SimpleRetriever,
            CustomPartitionRouter,
            False,
            ValueError,
            "LegacyToPerPartitionStateMigrations can only be applied with a parent stream configuration.",
        ),
    ],
)
def test_create_legacy_to_per_partition_state_migration(
    retriever_type,
    partition_router_class,
    is_parent_stream_config,
    expected_exception,
    expected_error_message,
):
    partition_router = partition_router_class(type="CustomPartitionRouter", class_name="a_class_namer") if partition_router_class else None

    stream = MagicMock()
    stream.retriever = MagicMock(spec=retriever_type)
    stream.retriever.partition_router = partition_router

    content = """
    state_migrations:
      - type: LegacyToPerPartitionStateMigration
    """

    resolved_manifest = resolver.preprocess_manifest(YamlDeclarativeSource._parse(content))
    state_migrations_manifest = transformer.propagate_types_and_parameters("", resolved_manifest["state_migrations"][0], {})

    if is_parent_stream_config:
        parent_stream_config = ParentStreamConfig(
            type="ParentStreamConfig",
            parent_key="id",
            partition_field="parent_id",
            stream=DeclarativeStream(
                type="DeclarativeStream", retriever=CustomRetriever(type="CustomRetriever", class_name="a_class_name")
            ),
        )
        partition_router.parent_stream_configs = [parent_stream_config]

    if expected_exception:
        with pytest.raises(expected_exception) as excinfo:
            factory.create_component(
                model_type=LegacyToPerPartitionStateMigrationModel,
                component_definition=state_migrations_manifest,
                config={},
                declarative_stream=stream,
            )
        assert str(excinfo.value) == expected_error_message
    else:
        migration_instance = factory.create_component(
            model_type=LegacyToPerPartitionStateMigrationModel,
            component_definition=state_migrations_manifest,
            config={},
            declarative_stream=stream,
        )
        assert migration_instance is not None
