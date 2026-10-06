#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from unittest.mock import Mock

from source_smartsheets.streams import SmartsheetStream

from airbyte_cdk.models import SyncMode


def test_state_saved_after_each_record(config, get_sheet_mocker):
    today_dt = datetime.datetime.now(datetime.timezone.utc)
    before_yesterday = (today_dt - datetime.timedelta(days=2)).isoformat(timespec="seconds")
    today = today_dt.isoformat(timespec="seconds")
    record = {"id": "1", "name": "Georgio", "last_name": "Armani", "modifiedAt": today}
    stream = SmartsheetStream(Mock(read_records=Mock(return_value=[record])), config)
    stream.state = {stream.cursor_field: before_yesterday}
    for _ in stream.read_records(SyncMode.incremental):
        assert _ == record
    assert stream.state == {stream.cursor_field: today}
