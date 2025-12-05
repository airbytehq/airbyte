#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest import TestCase

from airbyte_cdk.models import SyncMode
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput
from airbyte_cdk.test.mock_http import HttpMocker

from .config import CALL_ID, FOLDER_ID, ConfigBuilder
from .request_builder import RequestBuilder
from .response_builder import (
    empty_response,
    error_response,
    library_folder_content_response,
    library_folders_response,
)
from .utils import config, read_output


_STREAM_NAME = "libraryFolderContent"


def _read(
    config_builder: ConfigBuilder,
    sync_mode: SyncMode = SyncMode.full_refresh,
    expecting_exception: bool = False,
) -> EntrypointOutput:
    return read_output(
        config_builder=config_builder,
        stream_name=_STREAM_NAME,
        sync_mode=sync_mode,
        expecting_exception=expecting_exception,
    )


class TestLibraryFolderContent(TestCase):
    @HttpMocker()
    def test_read_records(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            RequestBuilder.library_folders_endpoint().build(),
            library_folders_response(folder_id=FOLDER_ID),
        )
        http_mocker.get(
            RequestBuilder.library_folder_content_endpoint(folder_id=FOLDER_ID).build(),
            library_folder_content_response(call_id=CALL_ID),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 1
        assert output.records[0].record.data["id"] == CALL_ID

    @HttpMocker()
    def test_read_records_empty_parent(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            RequestBuilder.library_folders_endpoint().build(),
            empty_response(stream_key="folders"),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_empty_content(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            RequestBuilder.library_folders_endpoint().build(),
            library_folders_response(folder_id=FOLDER_ID),
        )
        http_mocker.get(
            RequestBuilder.library_folder_content_endpoint(folder_id=FOLDER_ID).build(),
            empty_response(stream_key="calls"),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 0

    @HttpMocker()
    def test_read_records_multiple_folders(self, http_mocker: HttpMocker) -> None:
        folder_1 = "folder_1"
        folder_2 = "folder_2"
        http_mocker.get(
            RequestBuilder.library_folders_endpoint().build(),
            [
                library_folders_response(folder_id=folder_1, has_next=True, cursor="page2"),
                library_folders_response(folder_id=folder_2, has_next=False),
            ],
        )
        http_mocker.get(
            RequestBuilder.library_folder_content_endpoint(folder_id=folder_1).build(),
            library_folder_content_response(call_id="call_1"),
        )
        http_mocker.get(
            RequestBuilder.library_folder_content_endpoint(folder_id=folder_2).build(),
            library_folder_content_response(call_id="call_2"),
        )

        output = _read(config_builder=config())
        assert len(output.records) == 2

    @HttpMocker()
    def test_read_records_with_error_401(self, http_mocker: HttpMocker) -> None:
        http_mocker.get(
            RequestBuilder.library_folders_endpoint().build(),
            error_response(HTTPStatus.UNAUTHORIZED),
        )

        output = _read(config_builder=config(), expecting_exception=True)
        assert len(output.records) == 0
