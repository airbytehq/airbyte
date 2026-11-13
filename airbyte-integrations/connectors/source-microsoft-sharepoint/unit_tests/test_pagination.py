# Copyright (c) 2026 Airbyte, Inc., all rights reserved.
"""Folder enumeration must follow Microsoft Graph's @odata.nextLink (exercised with the real office365 client)."""

from unittest.mock import patch

import pytest
import requests_mock
from office365.graph_client import GraphClient
from source_microsoft_sharepoint.stream_reader import SourceMicrosoftSharePointStreamReader


DRIVE = "https://graph.microsoft.com/v1.0/drives/drive1"
JSON = {"Content-Type": "application/json"}


def _file(name):
    return {
        "id": name,
        "name": name,
        "file": {},
        "@microsoft.graph.downloadUrl": f"https://download/{name}",
        "lastModifiedDateTime": "2026-01-01T00:00:00Z",
        "createdDateTime": "2026-01-01T00:00:00Z",
    }


def _register_paged(mocker, url, items, page_size=200, throttled_page=None):
    """Serves `items` in pages linked by @odata.nextLink; `throttled_page` answers 429 once first."""
    pages = [items[i : i + page_size] for i in range(0, len(items), page_size)]
    for n, page in enumerate(pages):
        body = {"value": page}
        if n + 1 < len(pages):
            body["@odata.nextLink"] = f"{url}?$skiptoken={n + 1}"
        responses = [{"json": body, "headers": JSON}]
        if n == throttled_page:
            responses.insert(0, {"status_code": 429, "json": {}, "headers": {**JSON, "Retry-After": "1"}})
        mocker.get(url if n == 0 else f"{url}?$skiptoken={n}", responses, complete_qs=True)


@pytest.fixture
def root():
    return GraphClient(lambda: {"token_type": "Bearer", "access_token": "token"}).drives["drive1"].root


def test_list_directories_and_files_follows_next_link(root):
    folders = [{"id": f"f{i:03d}", "name": f"Client {i:03d}", "folder": {}} for i in range(450)]
    with requests_mock.Mocker() as m:
        _register_paged(m, f"{DRIVE}/root/children", folders)
        for folder in folders[:-1]:
            _register_paged(m, f"{DRIVE}/items/{folder['id']}/children", [_file(f"{folder['name']}.pdf")])
        _register_paged(m, f"{DRIVE}/items/f449/children", [_file(f"deck-{i:03d}.pptx") for i in range(250)])

        files = list(SourceMicrosoftSharePointStreamReader()._list_directories_and_files(root, "https://site"))

    assert len(files) == 449 + 250
    assert files[0].uri == "https://site/Client 000/Client 000.pdf"
    assert files[-1].uri == "https://site/Client 449/deck-249.pptx"


@patch("source_microsoft_sharepoint.utils.time.sleep")
def test_list_directories_and_files_retries_throttled_page(mock_sleep, root):
    with requests_mock.Mocker() as m:
        _register_paged(m, f"{DRIVE}/root/children", [_file(f"{i:03d}.pdf") for i in range(450)], throttled_page=1)
        files = list(SourceMicrosoftSharePointStreamReader()._list_directories_and_files(root, "https://site"))

    assert [f.uri for f in files] == [f"https://site/{i:03d}.pdf" for i in range(450)]
    mock_sleep.assert_called_once_with(1)
