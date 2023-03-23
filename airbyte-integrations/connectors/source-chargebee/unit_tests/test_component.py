#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import pytest
from source_chargebee.components import CustomFieldTransformation


@pytest.mark.parametrize(
    "record, expected_record",
    [
        ({'pk': 1, 'name': "example"}, {'pk': 1, 'name': "example", "custom_fields": []}),
        ({'pk': 1, 'name': "example", "cf_field1": "val1", "cf_field2": "val2"},
         {'pk': 1, 'name': "example", "cf_field1": "val1", "cf_field2": "val2",
          "custom_fields": [{"name": "cf_field1", "value": "val1"},
                            {"name": "cf_field2", "value": "val2"}]})
    ],
    ids=["no_custom_field", "custom_field"]
)
def test_field_transformation(record, expected_record):
    transformer = CustomFieldTransformation()
    transformed_record = transformer.transform(record)
    assert transformed_record == expected_record
