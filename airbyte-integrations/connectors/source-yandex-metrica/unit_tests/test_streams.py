#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from source_yandex_metrica.streams import Sessions

from airbyte_cdk.models import SyncMode


EXPECTED_RECORDS = [
    {"watchID": "00000000", "dateTime": "2022-09-01T12:00:00+00:00"},
    {"watchID": "00000001", "dateTime": "2022-08-01T12:00:10+00:00"},
]


def test_download_parse_response(config, mock_all_requests):
    stream = Sessions(config)
    records = list(stream.read_records(sync_mode=SyncMode.full_refresh))

    assert list(records) == EXPECTED_RECORDS


def test_state(config, mock_all_requests):
    stream = Sessions(config)
    list(stream.read_records(sync_mode=SyncMode.incremental))
    assert stream.state == {"dateTime": "2022-09-01T12:00:00+00:00"}
