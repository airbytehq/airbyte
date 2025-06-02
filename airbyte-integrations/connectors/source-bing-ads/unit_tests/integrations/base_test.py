# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
import json
import zipfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
from unittest import TestCase
from unittest.mock import MagicMock, patch

from bingads.v13.bulk import BulkServiceManager
from bingads.v13.reporting.reporting_service_manager import ReportingServiceManager
from client_builder import build_request, build_request_2, response_with_status
from config_builder import ConfigBuilder
from protocol_helpers import read_helper
from request_builder import RequestBuilder
from suds.transport.https import HttpAuthenticated
from suds_response_mock import mock_http_authenticated_send

from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, AirbyteStateMessage, Level, SyncMode, Type
from airbyte_cdk.test.catalog_builder import CatalogBuilder
from airbyte_cdk.test.entrypoint_wrapper import EntrypointOutput, read
from airbyte_cdk.test.mock_http import HttpMocker, HttpResponse
from airbyte_cdk.test.mock_http.response_builder import find_template
from airbyte_cdk.test.state_builder import StateBuilder


def create_zip_from_csv(filename: str) -> bytes:
    """
    Creates a zip file containing a CSV file from the resource/response folder.
    The CSV is stored directly in the zip without additional gzip compression.

    Args:
        filename: The name of the CSV file without extension

    Returns:
        The zip file content as bytes
    """
    # Build path to the CSV file in resource/response folder
    csv_path = Path(__file__).parent.parent / f"resource/response/{filename}.csv"

    # Read the CSV content
    with open(csv_path, "r") as csv_file:
        csv_content = csv_file.read()

    # Create a zip file containing the CSV file directly (without gzip compression)
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, mode="w") as zip_file:
        zip_file.writestr(f"{filename}.csv", csv_content)

    return zip_buffer.getvalue()


class BaseTest(TestCase):
    def setUp(self) -> None:
        self._http_mocker = HttpMocker()
        self._http_mocker.__enter__()

        self._auth_client(self._http_mocker)

    def tearDown(self) -> None:
        self._http_mocker.__exit__(None, None, None)

    @property
    def service_manager(self) -> Union[ReportingServiceManager, BulkServiceManager]:
        pass

    def _download_file(self, file: Optional[str] = None) -> Path:
        pass

    @property
    def _config(self) -> dict[str, Any]:
        return ConfigBuilder().build()

    def _state(self, file: str, stream_name: str) -> list[AirbyteStateMessage]:
        state_file = Path(__file__).parent.parent / f"resource/state/{file}.json"
        with open(state_file, "r") as f:
            state = json.loads(f.read())
            return StateBuilder().with_stream_state(stream_name, state).build()

    def _auth_client(self, http_mocker: HttpMocker) -> None:
        http_mocker.post(request=build_request(self._config), responses=response_with_status("oauth", 200))
        http_mocker.post(request=build_request_2(self._config), responses=response_with_status("oauth", 200))

    def mock_user_query_api(self, response_template: str) -> None:
        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource="User/Query").with_body('{"UserId": null}').build(),
            HttpResponse(json.dumps(find_template(response_template, __file__)), 200),
        )

    def mock_accounts_search_api(self, body: bytes, response_template: str) -> None:
        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource="Accounts/Search").with_body(body).build(),
            HttpResponse(json.dumps(find_template(resource=response_template, execution_folder=__file__)), 200),
        )

    def mock_generate_report_api(self, endpoint: str, body: bytes, response_template: str) -> None:
        http_mocker = self.http_mocker
        http_mocker.post(
            RequestBuilder(resource=f"GenerateReport/{endpoint}", api="reporting").with_body(body).build(),
            HttpResponse(json.dumps(find_template(resource=response_template, execution_folder=__file__)), 200),
        )

    def mock_get_report_request_api(self, file_name) -> None:
        zipped_data = create_zip_from_csv(file_name)
        http_mocker = self.http_mocker
        http_mocker.get(
            RequestBuilder(resource="").build_report_url(),
            HttpResponse(zipped_data),
        )

    def read_stream(
        self,
        stream_name: str,
        sync_mode: SyncMode,
        config: Dict[str, Any],
        stream_data_file: str = None,
        state: Optional[Dict[str, Any]] = None,
        expecting_exception: bool = False,
    ) -> Tuple[EntrypointOutput, MagicMock]:
        with patch.object(HttpAuthenticated, "send", mock_http_authenticated_send):
            with patch.object(
                self.service_manager, "download_file", return_value=self._download_file(stream_data_file)
            ) as service_call_mock:
                self.mock_get_report_request_api(stream_data_file)
                catalog = CatalogBuilder().with_stream(stream_name, sync_mode).build()
                return read_helper(config, catalog, state, expecting_exception), service_call_mock

    @property
    def http_mocker(self) -> HttpMocker:
        return self._http_mocker

    @staticmethod
    def create_log_message(log_message: str):
        return AirbyteMessage(
            type=Type.LOG,
            log=AirbyteLogMessage(
                level=Level.INFO,
                message=log_message,
            ),
        )
