#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from pytest import fixture
from source_yandex_metrica.streams import Sessions, Views


@fixture
def fixtures():
    kwargs = {"authenticator": TokenAuthenticator("MockOAuth2Token")}
    return {
        "views_stream": Views(
            counter_id=00000000,
            params={"start_date": "2022-07-01", "end_date": "2022-07-02", "fields": ["watchID", "dateTime"]},
            **kwargs,
        ),
        "sessions_stream": Sessions(
            counter_id=00000000,
            params={"start_date": "2022-07-01", "end_date": "2022-07-02", "fields": ["visitID", "dateTime"]},
            **kwargs,
        ),
    }


# Views stream tests
def test_views_cursor_field(fixtures):
    stream = fixtures["views_stream"]
    expected_cursor_field = "dateTime"

    assert stream.cursor_field == expected_cursor_field


def test_views_supports_incremental(fixtures):
    stream = fixtures["views_stream"]

    assert stream.supports_incremental


def test_views_source_defined_cursor(fixtures):
    stream = fixtures["views_stream"]

    assert stream.source_defined_cursor


def test_views_checkpoint_interval(fixtures):
    stream = fixtures["views_stream"]
    expected_checkpoint_interval = 20

    assert stream.state_checkpoint_interval == expected_checkpoint_interval


# Sessions stream tests
def test_sessions_cursor_field(fixtures):
    stream = fixtures["sessions_stream"]
    expected_cursor_field = "dateTime"

    assert stream.cursor_field == expected_cursor_field


def test_sessions_supports_incremental(fixtures):
    stream = fixtures["sessions_stream"]

    assert stream.supports_incremental


def test_sessions_source_defined_cursor(fixtures):
    stream = fixtures["sessions_stream"]

    assert stream.source_defined_cursor


def test_sessions_checkpoint_interval(fixtures):
    stream = fixtures["sessions_stream"]
    expected_checkpoint_interval = 20

    assert stream.state_checkpoint_interval == expected_checkpoint_interval
