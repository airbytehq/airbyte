#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
from unittest.mock import MagicMock, PropertyMock, patch

import pendulum
import pytest

import json
from typing import Any, Mapping

from airbyte_cdk.models import SyncMode
from source_snapchat_marketing.source import Adaccounts, Organizations, SnapchatAdsOauth2Authenticator, get_depend_on_ids, Stats, \
    AdaccountsStatsLifetime, AdaccountsStatsDaily, StatsIncremental


def _config() -> Mapping[str, Any]:
    """
    Get the config from /test_input
    """
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


config = _config()
created_streams = {}

kwargs = {"sync_mode": SyncMode.incremental, "cursor_field": "updated_at", "stream_state": None}

depends_on_stream_config = {"authenticator": SnapchatAdsOauth2Authenticator(config), "start_date": "2000-01-01", "end_date": "2000-01-10"}

expected_organization_ids = [{"organization_id": "7f064d90-52a1-42db-b25b-7539e663e926"}]
expected_adaccount_ids = [
    {"ad_account_id": "04214c00-3aa5-4123-b5c8-363c32c40e42"},
    {"ad_account_id": "e4cd371b-8de8-4011-a8d2-860fe77c09e1"},
]


def test_get_depend_on_ids_none():
    """Testing the stream that has non parent dependency (like Organizations has no dependency)"""
    # sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    depends_on_stream = None
    slice_key_name = None
    ids = get_depend_on_ids(depends_on_stream, depends_on_stream_config, slice_key_name)
    assert ids == [None]


def test_get_depend_on_ids_1():
    """Testing the stream that has 1 level parent dependency (like Adaccounts has dependency on Organizations)"""
    # sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    depends_on_stream = Organizations
    slice_key_name = "organization_id"
    ids = get_depend_on_ids(depends_on_stream, depends_on_stream_config, slice_key_name)
    assert ids == expected_organization_ids


def test_get_depend_on_ids_2():
    """
    Testing the that has 2 level parent dependency on organization ids
    (like Media has dependency on Adaccounts and Adaccounts has dependency on Organizations)
    """
    depends_on_stream = Adaccounts
    slice_key_name = "ad_account_id"
    ids = get_depend_on_ids(depends_on_stream, depends_on_stream_config, slice_key_name)
    assert ids == expected_adaccount_ids


stats_config = {
    "authenticator": SnapchatAdsOauth2Authenticator(config),
    "start_date": "2000-01-01",
    "end_date": "2000-02-10"
}
stats_stream = AdaccountsStatsDaily(**stats_config)


@pytest.mark.parametrize(
    "slice_period,expected_date_slices",
    [
        # for Hourly streams
        (7, [
            {'start_date': '2000-01-01', 'end_date': '2000-01-08'},
            {'start_date': '2000-01-08', 'end_date': '2000-01-15'},
            {'start_date': '2000-01-15', 'end_date': '2000-01-22'},
            {'start_date': '2000-01-22', 'end_date': '2000-01-29'},
            {'start_date': '2000-01-29', 'end_date': '2000-02-05'},
            {'start_date': '2000-02-05', 'end_date': '2000-02-10'},
        ]),
        # for Daily streams
        (31, [
            {'start_date': '2000-01-01', 'end_date': '2000-02-01'},
            {'start_date': '2000-02-01', 'end_date': '2000-02-10'},
        ]),
        # when start-end period == slice period
        (40, [
            {'start_date': '2000-01-01', 'end_date': '2000-02-10'},
        ]),
        # when start-end period > slice period
        (100, [
            {'start_date': '2000-01-01', 'end_date': '2000-02-10'},
        ]),
    ],
)
def test_date_slices(slice_period, expected_date_slices):
    stats_stream.slice_period = slice_period
    date_slices = stats_stream.date_slices()
    assert date_slices == expected_date_slices



def test_stream_slices_lifetime():
    stream = AdaccountsStatsLifetime(**stats_config)
    stream_slices = stream.stream_slices()
    assert list(stream_slices) == [
        {'id': '04214c00-3aa5-4123-b5c8-363c32c40e42'},
        {'id': 'e4cd371b-8de8-4011-a8d2-860fe77c09e1'}
    ]


def test_stream_slices_daily():
    stream = AdaccountsStatsDaily(**stats_config)
    stream_slices = stream.stream_slices()
    assert list(stream_slices) == [
        {'end_date': '2000-02-01',
         'id': '04214c00-3aa5-4123-b5c8-363c32c40e42',
         'start_date': '2000-01-01'},
        {'end_date': '2000-02-01',
         'id': 'e4cd371b-8de8-4011-a8d2-860fe77c09e1',
         'start_date': '2000-01-01'},
        {'end_date': '2000-02-10',
         'id': '04214c00-3aa5-4123-b5c8-363c32c40e42',
         'start_date': '2000-02-01'},
        {'end_date': '2000-02-10',
         'id': 'e4cd371b-8de8-4011-a8d2-860fe77c09e1',
         'start_date': '2000-02-01'}
    ]
