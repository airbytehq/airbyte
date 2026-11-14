#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os
from unittest.mock import patch

from source_facebook_pages.components import CustomFieldTransformation


def test_field_transformation():
    with (
        open(f"{os.path.dirname(__file__)}/initial_record.json", "r") as initial_record,
        open(f"{os.path.dirname(__file__)}/transformed_record.json", "r") as transformed_record,
    ):
        initial_record = json.loads(initial_record.read())
        transformed_record = json.loads(transformed_record.read())
        record_transformation = CustomFieldTransformation(config={}, parameters={"name": "page"})
        assert transformed_record == record_transformation.transform(initial_record)


def test_date_time_paths_are_resolved_once_across_transforms():
    with patch.object(
        CustomFieldTransformation,
        "_get_date_time_dpath_from_schema",
        wraps=CustomFieldTransformation._get_date_time_dpath_from_schema,
        autospec=True,
    ) as resolve_paths:
        record_transformation = CustomFieldTransformation(config={}, parameters={"name": "page"})
        for _ in range(3):
            record_transformation.transform({"id": "1", "created_time": "2024-01-01T00:00:00+0000"})

    assert resolve_paths.call_count == 1
