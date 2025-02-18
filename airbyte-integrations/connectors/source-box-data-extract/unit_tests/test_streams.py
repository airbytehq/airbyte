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
