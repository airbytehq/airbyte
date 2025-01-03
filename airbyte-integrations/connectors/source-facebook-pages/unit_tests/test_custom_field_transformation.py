#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import os

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
