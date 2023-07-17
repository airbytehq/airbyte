#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import timedelta

import pendulum
from airbyte_cdk.sources.streams.http.auth import NoAuth
from source_mixpanel.streams import Annotations, Export


def test_date_slices():

    now = pendulum.today(tz="US/Pacific").date()
    # Test with start_date now range
    stream_slices = Annotations(
        authenticator=NoAuth(), start_date=now, end_date=now, date_window_size=1, region="EU", project_timezone="US/Pacific"
    ).stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=now - timedelta(days=1),
        end_date=now,
        date_window_size=1,
        region="US",
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any")
    assert 2 == len(stream_slices)

    stream_slices = Annotations(
        authenticator=NoAuth(),
        region="US",
        start_date=now - timedelta(days=2),
        end_date=now,
        date_window_size=1,
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any")
    assert 3 == len(stream_slices)

    stream_slices = Annotations(
        authenticator=NoAuth(),
        region="US",
        start_date=now - timedelta(days=2),
        end_date=now,
        date_window_size=10,
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any")
    assert 1 == len(stream_slices)

    # test with attribution_window
    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=now - timedelta(days=2),
        end_date=now,
        date_window_size=1,
        attribution_window=5,
        region="US",
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any")
    assert 8 == len(stream_slices)

    # Test with start_date end_date range
    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=pendulum.datetime(2021, 7, 1, tz="US/Pacific"),
        end_date=pendulum.datetime(2021, 7, 1, tz="US/Pacific"),
        date_window_size=1,
        region="US",
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any")
    assert [
        {"start_date": pendulum.datetime(2021, 7, 1, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 1, tz="US/Pacific")}
    ] == stream_slices

    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=pendulum.datetime(2021, 7, 1, tz="US/Pacific"),
        end_date=pendulum.datetime(2021, 7, 2, tz="US/Pacific"),
        date_window_size=1,
        region="EU",
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any")
    assert [
        {"start_date": pendulum.datetime(2021, 7, 1, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 1, tz="US/Pacific")},
        {"start_date": pendulum.datetime(2021, 7, 2, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 2, tz="US/Pacific")}
    ] == stream_slices

    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=pendulum.datetime(2021, 7, 1, tz="US/Pacific"),
        end_date=pendulum.datetime(2021, 7, 3, tz="US/Pacific"),
        date_window_size=1,
        region="US",
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any")
    assert [
        {"start_date": pendulum.datetime(2021, 7, 1, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 1, tz="US/Pacific")},
        {"start_date": pendulum.datetime(2021, 7, 2, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 2, tz="US/Pacific")},
        {"start_date": pendulum.datetime(2021, 7, 3, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 3, tz="US/Pacific")},
    ] == stream_slices

    stream_slices = Annotations(
        authenticator=NoAuth(),
        start_date=pendulum.datetime(2021, 7, 1, tz="US/Pacific"),
        end_date=pendulum.datetime(2021, 7, 3, tz="US/Pacific"),
        date_window_size=2,
        region="US",
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any")
    assert [
        {"start_date": pendulum.datetime(2021, 7, 1, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 2, tz="US/Pacific")},
        {"start_date": pendulum.datetime(2021, 7, 3, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 3, tz="US/Pacific")}
    ] == stream_slices

    # test with stream_state
    stream_slices = Export(
        authenticator=NoAuth(),
        start_date=pendulum.datetime(2021, 7, 1, tz="US/Pacific"),
        end_date=pendulum.datetime(2021, 7, 3, tz="US/Pacific"),
        date_window_size=1,
        region="US",
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any", stream_state={"time": "2021-07-02T00:00:00-07:00"})
    assert [
        {"start_date": pendulum.datetime(2021, 7, 2, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 2, tz="US/Pacific")},
        {"start_date": pendulum.datetime(2021, 7, 3, tz="US/Pacific"), "end_date": pendulum.datetime(2021, 7, 3, tz="US/Pacific")}
    ] == stream_slices
