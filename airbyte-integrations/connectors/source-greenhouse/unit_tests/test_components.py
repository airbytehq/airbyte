#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock

from source_greenhouse.components import GreenhouseStateMigration


def test_migrate():
    declarative_stream = MagicMock()
    declarative_stream.retriever.partition_router.parent_stream_configs = [
        {"partition_field": "parent_id"},
    ]
    config = MagicMock()
    state_migrator = GreenhouseStateMigration(declarative_stream, config)

    stream_state = {
        "1111111111": {"updated_at": "2025-01-01T00:00:00.000Z"},
        "2222222222": {"updated_at": "2025-01-01T00:00:00.000Z"},
    }
    expected_state = {
        "states": [
            {"cursor": {"updated_at": "2025-01-01T00:00:00.000Z"}, "partition": {"parent_id": 1111111111, "parent_slice": {}}},
            {"cursor": {"updated_at": "2025-01-01T00:00:00.000Z"}, "partition": {"parent_id": 2222222222, "parent_slice": {}}},
        ]
    }
    migrated_state = state_migrator.migrate(stream_state)
    assert migrated_state == expected_state
