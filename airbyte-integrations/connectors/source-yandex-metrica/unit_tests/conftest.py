#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest


@pytest.fixture(name='config')
def config_fixture():
    return {
        "auth_token": "test_token",
        "counter_id": "00000000",
        "start_date": "2022-07-01",
        "end_date": "2022-07-02"
    }


@pytest.fixture(name='config_wrong_date')
def config_wrong_date_fixture():
    return {
        "auth_token": "test_token",
        "counter_id": "00000000",
        "start_date": "2022-07-02",
        "end_date": "2022-07-01"
    }


@pytest.fixture(name="mock_all_requests")
def mock_all_requests_fixture(requests_mock):
    requests_mock.register_uri("POST",
                               "https://api-metrica.yandex.net/management/v1/counter/00000000/logrequests",
                               json={"log_request": {"request_id": 1}})
    requests_mock.register_uri("GET",
                               "https://api-metrica.yandex.net/management/v1/counter/00000000/logrequest/1",
                               json={"log_request": {"status": "processed", "parts":[{"part_number": 0}]}})
    requests_mock.register_uri("GET",
                               'https://api-metrica.yandex.net/management/v1/counter/00000000/logrequest/1/part/0/download',
                               text="watchID\tdateTime\n00000000\t2022-09-01 12:00:00\n00000001\t2022-08-01 12:00:10")
    requests_mock.register_uri("POST",
                               'https://api-metrica.yandex.net/management/v1/counter/00000000/logrequest/1/clean',
                               status_code=200)
