from unittest import mock
from collections import defaultdict
import logging
from datetime import datetime

import pytest
from airbyte_cdk.models import Status

from source.source import RmsCloudApiKapicheSource, date_to_rms_string, date_ranges_generator

logger = logging.getLogger("airbyte")


def test_date_to_rms_string():
    d = datetime(year=2022, month=1, day=25, hour=20, minute=30)
    v = date_to_rms_string(d)
    assert v == "2022-01-25 20:30:00"


@pytest.mark.parametrize('start,end,span,first,last,n', [
    pytest.param(
        datetime(year=2022, month=1, day=1),
        datetime(year=2022, month=6, day=30),
        None,
        ('2022-01-01 00:00:00', '2022-01-08 00:00:00'),
        ('2022-06-25 00:00:00', '2022-07-02 00:00:00'),
        26,
        id="basic usage"
    ),
    pytest.param(
        datetime(year=2222, month=1, day=1),
        None,
        None,
        "doesn't matter",
        "doesn't matter",
        0,
        id="start date is in the future"
    ),
])
def test_date_ranges_generator(start, end, span, first, last, n):
    items = list(date_ranges_generator(
        start_date=start,
        end=end,
        span=span,
    ))
    assert len(items) == n
    if items:
        assert tuple(date_to_rms_string(x) for x in items[0]) == first
        assert tuple(date_to_rms_string(x) for x in items[-1]) == last


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
