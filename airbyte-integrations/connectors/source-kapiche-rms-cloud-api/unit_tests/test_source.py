from unittest import mock
from collections import defaultdict
import logging

import pytest
from airbyte_cdk.models import Status

from source.source import RmsCloudApiKapicheSource

logger = logging.getLogger("airbyte")


@pytest.mark.parametrize('side_effect,status', [
    ("123", Status.SUCCEEDED),
    (Exception("oops"), Status.FAILED)
])
def test_check_connection(side_effect, status):
    source = RmsCloudApiKapicheSource()
    with mock.patch(
        "source.source.RmsCloudApiKapicheSource.get_auth_token"
    ) as get_auth_token:
        get_auth_token.side_effect = side_effect
        result = source.check(logger, {})
        assert result.status is status


def test_discover():
    source = RmsCloudApiKapicheSource()
    config = defaultdict(str)
    catalog = source.discover(logger, config)
    assert catalog
    assert catalog.streams[0].name == "RMSNPS"
    """
    (Pdb++) catalog.streams[0].supported_sync_modes
    [<SyncMode.full_refresh: 'full_refresh'>, <SyncMode.incremental: 'incremental'>]
    (Pdb++) catalog.streams[0].source_defined_cursor
    False
    (Pdb++) catalog.streams[0].default_cursor_field
    (Pdb++) catalog.streams[0].source_defined_primary_key
    (Pdb++)
    """


# def test_streams(mocker):
#     source = RmsCloudApiKapicheSource()
#     with mock.patch("source_kapiche_export_api.source.ExportDataList") as list_endpoint:
#         config_mock = {
#             "api_token": "some-token",
#             "export_api_url": "https://app.kapiche/export.com",
#         }
#         list_stream_object = mock.MagicMock()
#         response = mock.MagicMock()
#         response.json.return_value = [
#             {
#                 "uuid": "uuid1",
#                 "export_url": "endpoint1",
#                 "project_name": "test1",
#                 "analysis_name": "test1",
#                 "enabled": False,
#             },
#             {
#                 "uuid": "uuid2",
#                 "export_url": "endpoint2",
#                 "project_name": "test2",
#                 "analysis_name": "test2",
#                 "enabled": True,
#             },
#         ]
#         response.status_code = 200
#         list_stream_object._send_request.return_value = response
#         list_endpoint.return_value = list_stream_object
#         streams = source.streams(config_mock)
#         assert len(streams) == 1
