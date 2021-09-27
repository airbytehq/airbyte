#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping

from airbyte_cdk.models import SyncMode
from source_snapchat_marketing.source import Adaccounts, Organizations, SnapchatAdsOauth2Authenticator, get_depend_on_ids


def _config() -> Mapping[str, Any]:
    """
    Get the config from /test_input
    """
    with open("secrets/config.json", "r") as f:
        return json.loads(f.read())


config = _config()
created_streams = {}

kwargs = {"sync_mode": SyncMode.incremental, "cursor_field": "updated_at", "stream_state": None}

depends_on_stream_config = {"authenticator": SnapchatAdsOauth2Authenticator(config), "start_date": "1970-01-01"}

expected_organization_ids = [{"organization_id": "7f064d90-52a1-42db-b25b-7539e663e926"}]
expected_adaccount_ids = [
    {"ad_account_id": "04214c00-3aa5-4123-b5c8-363c32c40e42"},
    {"ad_account_id": "e4cd371b-8de8-4011-a8d2-860fe77c09e1"},
]


def test_get_depend_on_ids_none():
    """ Testing the stream that has non parent dependency (like Organizations has no dependency) """
    # sync_mode: SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None
    depends_on_stream = None
    slice_key_name = None
    ids = get_depend_on_ids(depends_on_stream, depends_on_stream_config, slice_key_name)
    assert ids == [None]


def test_get_depend_on_ids_1():
    """ Testing the stream that has 1 level parent dependency (like Adaccounts has dependency on Organizations) """
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
