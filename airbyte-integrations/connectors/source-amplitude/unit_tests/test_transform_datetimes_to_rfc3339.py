#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import os
import re
import types
from contextlib import nullcontext as does_not_raise
from unittest.mock import MagicMock, patch

import pendulum
import pytest
import requests
import yaml
from source_amplitude.components import TransformDatetimesToRFC3339

from airbyte_cdk.utils import AirbyteTracedException


class TestTransformDatetimesToRFC3339:
    def test_transform(self):
        transformation = TransformDatetimesToRFC3339()
        record = {"event_time": "2021-01-01", "amplitude_id": 1234}
        transformed_record = transformation.transform(record)
        assert transformed_record == {"event_time": "2021-01-01T00:00:00+00:00", "amplitude_id": 1234}

    def test_transform_with_invalid_date(self):
        transformation = TransformDatetimesToRFC3339()
        record = {"event_time": "not a date", "amplitude_id": 1234}
        with pytest.raises(AirbyteTracedException):
            transformation.transform(record)

    def test_transform_with_null_date(self):
        transformation = TransformDatetimesToRFC3339()
        record = {"event_time": None, "amplitude_id": 1234}
        assert transformation.transform(record) == record

    def test_transform_with_no_dates_to_update(self):
        transformation = TransformDatetimesToRFC3339()
        record = {"amplitude_id": 1234}
        assert transformation.transform(record) == record
