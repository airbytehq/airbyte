from unittest import mock
from collections import defaultdict
import logging

import pytest
from airbyte_cdk.models import Status

from source.source import RmsCloudApiKapicheSource

logger = logging.getLogger("airbyte")


def test_check_connection():
    logger.info('blah')
    source = RmsCloudApiKapicheSource()
    with mock.patch(
        "source.source.RmsCloudApiKapicheSource.get_auth_token"
    ) as get_auth_token:
        get_auth_token.return_value = "123"
        result = source.check(logger, {})
        assert result.status is Status.SUCCEEDED


def test_discover():
    source = RmsCloudApiKapicheSource()
    config = defaultdict(str)
    catalog = source.discover(logger, config)
    print(catalog)
    assert catalog


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
