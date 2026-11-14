#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

# from http import HTTPStatus
from typing import Any, Mapping

# from unittest.mock import MagicMock
import pytest
from source_box_data_extract.box_api import get_box_ccg_client
from source_box_data_extract.source import StreamTextRepresentationFolder


@pytest.fixture
def sample_config() -> Mapping[str, Any]:
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "box_subject_type": "user",
        "box_subject_id": "test_box_subject_id",
        "folder_id": "test_folder_id",
    }


def test_stream_text_representation_folder(sample_config):
    client = get_box_ccg_client(sample_config)
    stream = StreamTextRepresentationFolder(client, sample_config["folder_id"])

    assert stream.folder_id == sample_config["folder_id"]
    assert stream.client == client
    assert stream.primary_key == "id"


def test_box_file_text_extract_triggers_generation_when_representation_missing(mocker):
    from unittest.mock import MagicMock

    from source_box_data_extract import box_api

    client = MagicMock()
    entry = MagicMock()
    entry.representation = "extracted_text"
    entry.status.state = "none"
    entry.info.url = "https://api.box.com/2.0/internal_files/1/versions/2/representations/extracted_text"
    entry.content.url_template = (
        "https://dl.boxcloud.com/api/2.0/internal_files/1/versions/2/representations/extracted_text/content/{+asset_path}"
    )
    client.files.get_file_by_id.return_value.representations.entries = [entry]
    do_request = mocker.patch.object(box_api, "_do_request", return_value=b"hello")

    assert box_api.box_file_text_extract(client, "1") == "hello"
    assert do_request.call_args_list[0].args == (client, entry.info.url)
    assert do_request.call_args_list[1].args == (client, entry.content.url_template.replace("{+asset_path}", ""))
