#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import date, timedelta

import pendulum
from source_mixpanel.streams import Export


def test_date_slices():

    now = pendulum.today(tz="US/Pacific").date()

    # test with stream_state
    stream_slices = Export(
        authenticator=None,
        start_date=date.fromisoformat("2021-07-01"),
        end_date=date.fromisoformat("2021-07-03"),
        date_window_size=1,
        region="US",
        project_timezone="US/Pacific",
    ).stream_slices(sync_mode="any", stream_state={"time": "2021-07-02T00:00:00Z"})
    assert [
        {"start_date": "2021-07-02", "end_date": "2021-07-02", "time": "2021-07-02T00:00:00Z"},
        {"start_date": "2021-07-03", "end_date": "2021-07-03", "time": "2021-07-02T00:00:00Z"},
    ] == list(stream_slices)
