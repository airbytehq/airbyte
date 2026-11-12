#
# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
#

import datetime
import logging

import pytest
from source_faker import SourceFaker

from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStreamSerializer, Type


def read_users(config, state=None):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStreamSerializer.load(
                {
                    "stream": {
                        "name": "users",
                        "json_schema": {"type": "object", "properties": {}},
                        "supported_sync_modes": ["incremental"],
                    },
                    "sync_mode": "incremental",
                    "destination_sync_mode": "overwrite",
                }
            )
        ]
    )
    return SourceFaker().read(logging.getLogger(__name__), config, catalog, state or [])


@pytest.mark.parametrize("always_updated", [True, False])
@pytest.mark.parametrize("count", [0, 1000])
def test_consecutive_syncs(mocker, always_updated, count):
    config = {"count": count, "seed": -1, "records_per_slice": 1000, "always_updated": always_updated, "parallelism": 4}
    clock = mocker.patch("source_faker.user_generator.datetime")
    clock.datetime.now.return_value = datetime.datetime(2026, 11, 10)
    first = list(read_users(config))
    first_records = [row.record.data for row in first if row.type == Type.RECORD]
    state = [row.state for row in first if row.type == Type.STATE][-1:]
    assert len(first_records) == count
    assert state[0].stream.stream_state.__dict__["loop_offset"] == count

    clock.datetime.now.return_value = datetime.datetime(2026, 11, 11)
    second = list(read_users(config, state))
    second_records = [row.record.data for row in second if row.type == Type.RECORD]
    assert len(second_records) == (count if always_updated else 0)
    if always_updated and count:
        assert [row["id"] for row in second_records] == [row["id"] for row in first_records]
        assert min(row["updated_at"] for row in second_records) > max(row["updated_at"] for row in first_records)


@pytest.mark.parametrize("offset", [100, 500])
@pytest.mark.parametrize("always_updated", [True, False])
def test_resume_from_checkpoint(offset, always_updated):
    config = {"count": 1000, "seed": -1, "records_per_slice": 100, "always_updated": always_updated, "parallelism": 4}
    iterator = read_users(config)
    emitted_ids = []
    try:
        for row in iterator:
            if row.type == Type.RECORD:
                emitted_ids.append(row.record.data["id"])
            elif row.type == Type.STATE and row.state.stream.stream_state.__dict__.get("loop_offset") == offset:
                checkpoint = row.state
                break
        else:
            pytest.fail("No mid-sync checkpoint emitted")
    finally:
        iterator.close()

    checkpointed_ids = emitted_ids[:offset]
    assert checkpointed_ids == list(range(1, offset + 1))
    resumed = list(read_users(config, [checkpoint]))
    resumed_ids = [row.record.data["id"] for row in resumed if row.type == Type.RECORD]
    assert resumed_ids == (list(range(offset + 1, 1001)) if always_updated else [])
    assert not set(checkpointed_ids).intersection(resumed_ids)
