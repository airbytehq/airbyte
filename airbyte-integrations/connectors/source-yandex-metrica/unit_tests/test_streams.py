#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from source_yandex_metrica.streams import Sessions


def test_download_parse_response(config, requests_mock):
    stream = Sessions(config)
    expected_records = [
        {"watchID": "00000000", "dateTime": "2022-07-01T12:00:00+00:00"},
        {"watchID": "00000001", "dateTime": "2022-07-01T12:00:10+00:00"}
    ]
    requests_mock.register_uri("GET",
                               'https://api-metrica.yandex.net/management/v1/counter/00000000/logrequest/0/part/0/download',
                               text="watchID\tdateTime\n00000000\t2022-07-01 12:00:00\n00000001\t2022-07-01 12:00:10")
    download_report = stream.download_report_part("0", 0)

    assert list(download_report) == expected_records
