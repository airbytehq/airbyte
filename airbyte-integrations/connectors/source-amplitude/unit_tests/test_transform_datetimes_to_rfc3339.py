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
