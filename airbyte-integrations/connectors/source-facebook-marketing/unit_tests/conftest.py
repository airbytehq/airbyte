#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from pytest import fixture


@fixture(autouse=True)
def time_sleep_mock(mocker):
    time_mock = mocker.patch("time.sleep")
    yield time_mock
