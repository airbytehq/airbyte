# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from unittest.mock import MagicMock

import pytest
from source_klaviyo.components.archived_to_per_partition_state_migration import (
    ArchivedToPerPartitionStateMigration,
    CampaignsStateMigration,
)


@pytest.mark.parametrize(
    ("state", "should_migrate"),
    (
        ({"updated_at": "2120-10-10T00:00:00+00:00", "archived": {"updated_at": "2020-10-10T00:00:00+00:00"}}, True),
        ({"updated_at": "2120-10-10T00:00:00+00:00"}, True),
        ({}, False),
        (
            {
                "states": [
                    {"partition": {"archived": "true", "campaign_type": "sms"}, "cursor": {"updated_at": "2023-10-10T00:00:00+0000"}},
                    {"partition": {"archived": "false", "campaign_type": "sms"}, "cursor": {"updated_at": "2023-10-10T00:00:00+0000"}},
                    {"partition": {"archived": "true", "campaign_type": "email"}, "cursor": {"updated_at": "2023-10-10T00:00:00+0000"}},
                    {"partition": {"archived": "false", "campaign_type": "email"}, "cursor": {"updated_at": "2023-10-10T00:00:00+0000"}},
                ]
            },
            False,
        ),
    ),
)
def test_should_migrate(state, should_migrate):
    config = {}
    declarative_stream = MagicMock()
    state_migrator = ArchivedToPerPartitionStateMigration(config=config, declarative_stream=declarative_stream)
    assert state_migrator.should_migrate(state) == should_migrate


@pytest.mark.parametrize(
    ("state", "expected_state"),
    (
        (
            {"updated_at": "2120-10-10T00:00:00+00:00", "archived": {"updated_at": "2020-10-10T00:00:00+00:00"}},
            {
                "states": [
                    {"cursor": {"updated_at": "2020-10-10T00:00:00+00:00"}, "partition": {"archived": "true"}},
                    {"cursor": {"updated_at": "2120-10-10T00:00:00+00:00"}, "partition": {"archived": "false"}},
                ]
            },
        ),
        (
            {"archived": {"updated_at": "2020-10-10T00:00:00+00:00"}},
            {
                "states": [
                    {"cursor": {"updated_at": "2020-10-10T00:00:00+00:00"}, "partition": {"archived": "true"}},
                    {"cursor": {"updated_at": "2012-01-01T00:00:00Z"}, "partition": {"archived": "false"}},
                ]
            },
        ),
        (
            {"updated_at": "2120-10-10T00:00:00+00:00"},
            {
                "states": [
                    {"cursor": {"updated_at": "2012-01-01T00:00:00Z"}, "partition": {"archived": "true"}},
                    {"cursor": {"updated_at": "2120-10-10T00:00:00+00:00"}, "partition": {"archived": "false"}},
                ]
            },
        ),
    ),
)
def test_migrate(state, expected_state):
    config = {}
    declarative_stream = MagicMock()
    declarative_stream.incremental_sync.cursor_field = "updated_at"
    state_migrator = ArchivedToPerPartitionStateMigration(config=config, declarative_stream=declarative_stream)
    assert state_migrator.migrate(state) == expected_state


@pytest.mark.parametrize(
    ("state", "expected_state"),
    (
        (
            {"updated_at": "2120-10-10T00:00:00+00:00", "archived": {"updated_at": "2020-10-10T00:00:00+00:00"}},
            {
                "states": [
                    {"cursor": {"updated_at": "2020-10-10T00:00:00+00:00"}, "partition": {"archived": "true", "campaign_type": "email"}},
                    {"cursor": {"updated_at": "2120-10-10T00:00:00+00:00"}, "partition": {"archived": "false", "campaign_type": "email"}},
                ]
            },
        ),
        (
            {"archived": {"updated_at": "2020-10-10T00:00:00+00:00"}},
            {
                "states": [
                    {"cursor": {"updated_at": "2020-10-10T00:00:00+00:00"}, "partition": {"archived": "true", "campaign_type": "email"}},
                    {"cursor": {"updated_at": "2012-01-01T00:00:00Z"}, "partition": {"archived": "false", "campaign_type": "email"}},
                ]
            },
        ),
        (
            {
                "updated_at": "2120-10-10T00:00:00+00:00",
            },
            {
                "states": [
                    {"cursor": {"updated_at": "2012-01-01T00:00:00Z"}, "partition": {"archived": "true", "campaign_type": "email"}},
                    {"cursor": {"updated_at": "2120-10-10T00:00:00+00:00"}, "partition": {"archived": "false", "campaign_type": "email"}},
                ]
            },
        ),
    ),
)
def test_migrate_campaigns(state, expected_state):
    config = {}
    declarative_stream = MagicMock()
    declarative_stream.incremental_sync.cursor_field = "updated_at"
    state_migrator = CampaignsStateMigration(config=config, declarative_stream=declarative_stream)
    assert state_migrator.migrate(state) == expected_state
