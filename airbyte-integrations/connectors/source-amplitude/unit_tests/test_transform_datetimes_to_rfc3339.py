#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#
import json

import pytest
from source_amplitude.components import TransformDatetimesToRFC3339

from airbyte_cdk.utils import AirbyteTracedException


class TestTransformDatetimesToRFC3339:
    def test_transform(self):
        record = {"event_time": "2021-01-01", "amplitude_id": 1234}
        transformed_record = TransformDatetimesToRFC3339().transform(record)
        assert transformed_record == {"event_time": "2021-01-01T00:00:00+00:00", "amplitude_id": 1234}

    def test_transform_with_invalid_date(self):
        record = {"event_time": "not a date", "amplitude_id": 1234}
        with pytest.raises(AirbyteTracedException):
            TransformDatetimesToRFC3339().transform(record)

    def test_transform_with_null_date(self):
        record = {"event_time": None, "amplitude_id": 1234}
        assert TransformDatetimesToRFC3339().transform(record) == record

    def test_transform_with_no_dates_to_update(self):
        record = {"amplitude_id": 1234}
        assert TransformDatetimesToRFC3339().transform(record) == record

    def test_get_schema(self):
        schema = TransformDatetimesToRFC3339()._get_schema(config={})
        assert schema.get("$schema")
        assert schema.get("type") == "object"
        assert schema.get("properties", {}).get("server_upload_time")

    def test_get_date_time_items_from_schema(self):
        date_time_items = TransformDatetimesToRFC3339()._get_date_time_items_from_schema(config={})

        assert len(date_time_items) == 7
        assert all(
            item in date_time_items
            for item in [
                "event_time",
                "server_upload_time",
                "processed_time",
                "server_received_time",
                "user_creation_time",
                "client_upload_time",
                "client_event_time",
            ]
        )
