# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import re

import pytest
import requests_mock
from conftest import get_source

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import read


_CONFIG = {
    "api_key": "test_api_key",
    "user_id": "test_user_id",
    "start_date": "2026-01-01T00:00:00Z",
}
_APPS_URL = re.compile(r"https://api\.clarifai\.com/v2/users/test_user_id/apps(?:\?.*)?$")


def _apps_page():
    return {
        "apps": [
            {"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"},
            {"id": "app2", "modified_at": "2026-10-14T09:41:55.568082659Z"},
        ]
    }


def test_applications_state_advances_to_newest_nanosecond_modified_at():
    catalog = CatalogBuilder().with_stream("applications", SyncMode.incremental).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json=_apps_page())
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == ["app1", "app2"]
    final_state = output.most_recent_state.stream_state.__dict__
    assert final_state == {"modified_at": "2026-10-14T09:41:55.568082Z"}


@pytest.mark.parametrize("stream_name,path", [("datasets", "datasets"), ("models", "models")])
def test_app_substream_state_advances_per_partition(stream_name, path):
    catalog = CatalogBuilder().with_stream(stream_name, SyncMode.incremental).build()

    with requests_mock.Mocker() as mocker:
        mocker.get(_APPS_URL, json={"apps": [{"id": "app1", "modified_at": "2026-10-02T17:05:11.904417302Z"}]})
        mocker.get(
            re.compile(rf"https://api\.clarifai\.com/v2/users/test_user_id/apps/app1/{path}(?:\?.*)?$"),
            json={path: [{"id": f"{path}-1", "modified_at": "2026-10-14T09:41:55.568082659Z"}]},
        )
        output = read(get_source(_CONFIG), config=_CONFIG, catalog=catalog)

    assert [record.record.data["id"] for record in output.records] == [f"{path}-1"]
    states = output.most_recent_state.stream_state.__dict__["states"]
    assert [(s["partition"]["app_id"], s["cursor"]["modified_at"]) for s in states] == [("app1", "2026-10-14T09:41:55.568082Z")]
