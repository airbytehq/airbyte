#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import json
import operator
from pathlib import Path

import pytest
from source_amplitude.source import SourceAmplitude

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.test.catalog_builder import CatalogBuilder


@pytest.fixture(scope="module")
def config():
    with open(Path(__file__).parent.parent / "secrets/config.json", "r") as file:
        return json.loads(file.read())


@pytest.fixture(scope="module")
def streams(config):
    catalog = (
        CatalogBuilder()
        .with_stream("annotations_stream", sync_mode=SyncMode.full_refresh)
        .with_stream("cohorts_stream", sync_mode=SyncMode.full_refresh)
        .build()
    )
    return SourceAmplitude(catalog=catalog, config=config, state={}).streams(config=config)


@pytest.fixture(scope="module")
def annotations_stream(streams):
    return next(filter(lambda s: s.name == "annotations", streams))


@pytest.fixture(scope="module")
def cohorts_stream(streams):
    return next(filter(lambda s: s.name == "cohorts", streams))


@pytest.mark.parametrize(
    "stream_fixture_name, url, expected_records",
    [
        (
            "annotations_stream",
            "https://amplitude.com/api/2/annotations",
            [
                {"date": "2023-09-22", "details": "vacate et scire", "id": 1, "label": "veritas"},
                {"date": "2023-09-22", "details": "valenter volenter", "id": 2, "label": "veritas"},
            ],
        ),
        (
            "cohorts_stream",
            "https://amplitude.com/api/3/cohorts",
            [
                {
                    "appId": 1,
                    "archived": False,
                    "chart_id": "27f310c471e8409797a18f18fe2884fb",
                    "createdAt": 1695394830,
                    "definition": {},
                    "description": "Arduus ad Solem",
                    "edit_id": "fab12bc14de641589630c2ceced1c197",
                    "finished": True,
                    "hidden": False,
                    "id": 1,
                    "is_official_content": True,
                    "is_predictive": True,
                    "last_viewed": 1695394946,
                    "lastComputed": 1695394830,
                    "lastMod": 1695394830,
                    "location_id": "517974113223461a8468400b6ce88383",
                    "metadata": ["me", "ta", "da", "ta"],
                    "name": "Solem",
                    "owners": ["me", "mom"],
                    "popularity": 100,
                    "published": True,
                    "shortcut_ids": ["solem"],
                    "size": 186,
                    "type": "one",
                    "view_count": 2,
                    "viewers": ["me", "mom"],
                }
            ],
        ),
    ],
)
def test_empty_streams(stream_fixture_name, url, expected_records, request, requests_mock):
    """
    A test with synthetic data since we are not able to test `annotations_stream` and `cohorts_stream` streams
    due to free subscription plan for the sandbox
    """
    stream = request.getfixturevalue(stream_fixture_name)
    empty_stream_slice = StreamSlice(partition={}, cursor_slice={})
    records_reader = stream.read_records(sync_mode=SyncMode.full_refresh, cursor_field=None, stream_slice=empty_stream_slice)
    requests_mock.get(url, status_code=200, json={"data": expected_records})

    # Sort actual and expected records by ID.
    # Prepare pairs of the actual and expected versions of the same record.
    pairs = zip(*[sorted(record, key=operator.itemgetter("id")) for record in (list(records_reader), expected_records)])

    # Calculate unmatched records and return their key, actual value and expected value
    unmatched = [
        [(key, _actual[key], _expected[key]) for key in _actual if _actual[key] != _expected[key]]
        for _actual, _expected in pairs
        if _actual != _expected
    ]

    # Ensure we don't have any unmatched records
    assert not any(unmatched)
