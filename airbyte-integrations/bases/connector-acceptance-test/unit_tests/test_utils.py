#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import random
import string
import tempfile
import time
from functools import partial
from pathlib import Path
from typing import Iterable
from unittest.mock import Mock

import pytest
import yaml
from connector_acceptance_test.config import EmptyStreamConfiguration
from connector_acceptance_test.utils import common
from connector_acceptance_test.utils.compare import make_hashable

from airbyte_protocol.models import AirbyteStream, ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, DestinationSyncMode, SyncMode


def not_sorted_data():
    return {
        "date_created": "0001-01-01T00:00:00",
        "date_updated": "0001-01-01T00:00:00",
        "editable": False,
        "id": "superuser",
        "name": "Super User",
        "organization_id": "orga_ya3w9oMjeLtWe7zFGZr63Dz8ruBbjybG0EIUdUXaESi",
        "permissions": [
            "bulk_edit",
            "delete_own_opportunities",
            "export",
            "manage_group_numbers",
            "manage_email_sequences",
            "delete_leads",
            "call_coach_listen",
            "call_coach_barge",
            "manage_others_tasks",
            "manage_others_activities",
            "delete_own_tasks",
            "manage_customizations",
            "manage_team_smart_views",
            "bulk_delete",
            "manage_team_email_templates",
            "bulk_email",
            "merge_leads",
            "calling",
            "bulk_sequence_subscriptions",
            "bulk_import",
            "delete_own_activities",
            "manage_others_opportunities",
        ],
    }


def sorted_data():
    return {
        "date_created": "0001-01-01T00:00:00",
        "date_updated": "0001-01-01T00:00:00",
        "editable": False,
        "id": "superuser",
        "name": "Super User",
        "organization_id": "orga_ya3w9oMjeLtWe7zFGZr63Dz8ruBbjybG0EIUdUXaESi",
        "permissions": [
            "bulk_delete",
            "bulk_edit",
            "bulk_email",
            "bulk_import",
            "bulk_sequence_subscriptions",
            "call_coach_barge",
            "call_coach_listen",
            "calling",
            "delete_leads",
            "delete_own_activities",
            "delete_own_opportunities",
            "delete_own_tasks",
            "export",
            "manage_customizations",
            "manage_email_sequences",
            "manage_group_numbers",
            "manage_others_activities",
            "manage_others_opportunities",
            "manage_others_tasks",
            "manage_team_email_templates",
            "manage_team_smart_views",
            "merge_leads",
        ],
    }


@pytest.mark.parametrize(
    "obj1,obj2,is_same",
    [
        (sorted_data(), not_sorted_data(), True),
        (
            {
                "organization": {
                    "features": [
                        "issue-percent-filters",
                        "performance-tag-page",
                    ]
                }
            },
            {
                "organization": {
                    "features": [
                        "performance-tag-page",
                        "issue-percent-filters",
                    ]
                }
            },
            True,
        ),
        (
            {
                "organization": {
                    "features": [
                        "issue-percent-filters",
                        "performance-tag-page",
                    ]
                }
            },
            {
                "organization": {
                    "features": [
                        "performance-tag-pag",
                        "issue-percent-filters",
                    ]
                }
            },
            False,
        ),
        (
            {
                "organization": {
                    "features": [
                        "issue-percent-filters",
                        "performance-tag-page",
                    ]
                }
            },
            {
                "organization": {
                    "features": [
                        "performance-tag-page",
                    ]
                }
            },
            False,
        ),
        ({"a": 1, "b": 2}, {"b": 2, "a": 1}, True),
        ({"a": 1, "b": 2, "c": {"d": [1, 2]}}, {"b": 2, "a": 1, "c": {"d": [2, 1]}}, True),
        ({"a": 1, "b": 2, "c": {"d": [1, 2]}}, {"b": 2, "a": 1, "c": {"d": [3, 4]}}, False),
    ],
)
def test_compare_two_records_nested_with_different_orders(obj1, obj2, is_same):
    """Test that compare two records with equals, not sorted data."""
    output_diff = set(map(make_hashable, [obj1])).symmetric_difference(set(map(make_hashable, [obj2])))
    if is_same:
        assert not output_diff, f"{obj1} should be equal to {obj2}"
    else:
        assert output_diff, f"{obj1} shouldnt be equal to {obj2}"


class MockContainer:
    def __init__(self, status: dict, iter_logs: Iterable):
        self.wait = Mock(return_value=status)
        self.logs = Mock(return_value=iter(iter_logs))
        self.remove = Mock()

        class Image:
            pass

        self.image = Image()


def binary_generator(lengths, last_line=None):
    data = ""
    for length in lengths:
        data += "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(length)) + "\n"
    data = data.encode()
    chunk_size = random.randint(2, 32)

    while len(data) > chunk_size:
        yield data[:chunk_size]
        data = data[chunk_size:]
    yield data
    if last_line:
        yield ("bla-1234567890-bla\n" + last_line).encode()


def wait_status(container, expected_statuses):
    """Waits expected_statuses for 5 sec"""
    for _ in range(500):
        if container.status in expected_statuses:
            return
        time.sleep(0.01)
    assert False, f"container of the image {container.image} has the status '{container.status}', "
    f"expected statuses: {expected_statuses}"


class TestLoadYamlOrJsonPath:
    VALID_SPEC = {
        "documentationUrl": "https://google.com",
        "connectionSpecification": {
            "type": "object",
            "required": ["api_token"],
            "additionalProperties": False,
            "properties": {"api_token": {"type": "string"}},
        },
    }

    def test_load_json(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json") as f:
            f.write(json.dumps(self.VALID_SPEC))
            f.flush()
            actual = common.load_yaml_or_json_path(Path(f.name))
            assert actual == self.VALID_SPEC

    def test_load_yaml(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml") as f:
            f.write(yaml.dump(self.VALID_SPEC))
            f.flush()
            actual = common.load_yaml_or_json_path(Path(f.name))
            assert actual == self.VALID_SPEC

    def test_load_other(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt") as f:
            with pytest.raises(RuntimeError):
                common.load_yaml_or_json_path(Path(f.name))


@pytest.mark.parametrize(
    "schema, searched_key, expected_values",
    [
        (
            {
                "looking_for_this_key": "first_match",
                "foo": "bar",
                "bar": {"looking_for_this_key": "second_match"},
                "top_level_list": [
                    {"looking_for_this_key": "third_match"},
                    {"looking_for_this_key": "fourth_match"},
                    "dump_value",
                    {"nested_in_list": {"looking_for_this_key": "fifth_match"}},
                ],
            },
            "looking_for_this_key",
            ["first_match", "second_match", "third_match", "fourth_match", "fifth_match"],
        ),
        ({"foo": "bar", "bar": {"looking_for_this_key": "single_match"}}, "looking_for_this_key", ["single_match"]),
        (
            ["foo", "bar", {"looking_for_this_key": "first_match"}, [{"looking_for_this_key": "second_match"}]],
            "looking_for_this_key",
            ["first_match", "second_match"],
        ),
    ],
)
def test_find_all_values_for_key_in_schema(schema, searched_key, expected_values):
    assert list(common.find_all_values_for_key_in_schema(schema, searched_key)) == expected_values


DUMMY_DISCOVERED_CATALOG = {
    "stream_a": AirbyteStream(
        name="stream_a",
        json_schema={"a": {"type": "string"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
    "stream_b": AirbyteStream(
        name="stream_b",
        json_schema={"a": {"type": "string"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
}

DUMMY_CUSTOM_CATALOG = {
    "stream_a": AirbyteStream(
        name="stream_a",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
    "stream_b": AirbyteStream(
        name="stream_b",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
}

DUMMY_CUSTOM_CATALOG_WITH_EXTRA_STREAM = {
    "stream_a": AirbyteStream(
        name="stream_a",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
    "stream_b": AirbyteStream(
        name="stream_b",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
    "stream_c": AirbyteStream(
        name="stream_c",
        json_schema={"a": {"type": "number"}},
        supported_sync_modes=[SyncMode.full_refresh],
    ),
}


@pytest.mark.parametrize(
    "discovered_catalog, empty_streams",
    [
        (DUMMY_DISCOVERED_CATALOG, set()),
        (DUMMY_DISCOVERED_CATALOG, {EmptyStreamConfiguration(name="stream_b", bypass_reason="foobar")}),
    ],
)
def test_build_configured_catalog_from_discovered_catalog_and_empty_streams(mocker, discovered_catalog, empty_streams):
    mocker.patch.object(common, "logging")
    configured_catalog = common.build_configured_catalog_from_discovered_catalog_and_empty_streams(discovered_catalog, empty_streams)
    assert len(configured_catalog.streams) == len(DUMMY_DISCOVERED_CATALOG.values()) - len(empty_streams)
    if empty_streams:
        common.logging.warning.assert_called_once()
        configured_stream_names = [configured_stream.stream.name for configured_stream in configured_catalog.streams]
        for empty_stream in empty_streams:
            assert empty_stream.name not in configured_stream_names
    else:
        common.logging.info.assert_called_once()


@pytest.mark.parametrize(
    "custom_configured_catalog, expect_failure", [(DUMMY_CUSTOM_CATALOG, False), (DUMMY_CUSTOM_CATALOG_WITH_EXTRA_STREAM, True)]
)
def test_build_configured_catalog_from_custom_catalog(mocker, custom_configured_catalog, expect_failure):
    mocker.patch.object(common, "logging")
    mocker.patch.object(common.pytest, "fail")

    dummy_configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(stream=stream, sync_mode=SyncMode.full_refresh, destination_sync_mode=DestinationSyncMode.append)
            for stream in custom_configured_catalog.values()
        ]
    )
    mocker.patch.object(common.ConfiguredAirbyteCatalog, "parse_file", mocker.Mock(return_value=dummy_configured_catalog))

    configured_catalog = common.build_configured_catalog_from_custom_catalog("path", DUMMY_DISCOVERED_CATALOG)

    if not expect_failure:
        assert len(configured_catalog.streams) == len(dummy_configured_catalog.streams)
        # Checking that the function under test retrieves the stream from the discovered catalog
        assert configured_catalog.streams[0].stream == DUMMY_DISCOVERED_CATALOG["stream_a"]
        assert configured_catalog.streams[0].stream != custom_configured_catalog["stream_a"]
        common.logging.info.assert_called_once()
    else:
        common.pytest.fail.assert_called_once()
