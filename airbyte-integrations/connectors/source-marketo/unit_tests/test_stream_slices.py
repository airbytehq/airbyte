#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from unittest.mock import ANY

from airbyte_cdk.models.airbyte_protocol import SyncMode


def test_create_export_job(send_email_stream, caplog):
    slices = list(send_email_stream.stream_slices(sync_mode=SyncMode.incremental))
    assert slices == [
        {"endAt": ANY, "id": "2c09ce6d", "startAt": ANY},
        {"endAt": ANY, "id": "cd465f55", "startAt": ANY},
        {"endAt": ANY, "id": "232aafb4", "startAt": ANY},
    ]
    assert "Filed to create export job for data slice " in caplog.records[-1].message
