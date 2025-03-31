#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
import pytest
from source_hubspot.components import NewtoLegacyFieldTransformation
from source_hubspot.streams import DEALS_NEW_TO_LEGACY_FIELDS_MAPPING


@pytest.mark.parametrize(
    "input, expected",
    [
        (
            {
                "name": {"type": ["null", "string"]},
                "hs_v2_cumulative_time_in_prospect": {"type": ["null", "string"]},
                "hs_v2_date_entered_prospect": {"type": ["null", "string"]},
                "hs_v2_date_exited_prospect": {"type": ["null", "string"]},
                "hs_v2_some_other_field": {"type": ["null", "string"]},
            },
            {
                "name": {"type": ["null", "string"]},
                "hs_v2_cumulative_time_in_prospect": {"type": ["null", "string"]},
                "hs_v2_date_entered_prospect": {"type": ["null", "string"]},
                "hs_date_entered_prospect": {"type": ["null", "string"]},
                "hs_v2_date_exited_prospect": {"type": ["null", "string"]},
                "hs_date_exited_prospect": {"type": ["null", "string"]},
                "hs_v2_some_other_field": {"type": ["null", "string"]},
            },
        ),
        (
            {"name": "Edgar Allen Poe", "age": 215, "birthplace": "Boston", "hs_v2_date_entered_poetry": 1827},
            {
                "name": "Edgar Allen Poe",
                "age": 215,
                "birthplace": "Boston",
                "hs_v2_date_entered_poetry": 1827,
                "hs_date_entered_poetry": 1827,
            },
        ),
        (
            {"name": "Edgar Allen Poe", "age": 215, "birthplace": "Boston", "properties": {"hs_v2_date_entered_poetry": 1827}},
            {
                "name": "Edgar Allen Poe",
                "age": 215,
                "birthplace": "Boston",
                "properties": {
                    "hs_v2_date_entered_poetry": 1827,
                    "hs_date_entered_poetry": 1827,
                },
            },
        ),
        (
            {
                "name": "Edgar Allen Poe",
                "age": 215,
                "birthplace": "Boston",
            },
            {
                "name": "Edgar Allen Poe",
                "age": 215,
                "birthplace": "Boston",
            },
        ),
        (
            {"name": "Edgar Allen Poe", "hs_v2_date_entered_poetry": 1827, "hs_date_entered_poetry": 9999},
            {
                "name": "Edgar Allen Poe",
                "hs_v2_date_entered_poetry": 1827,
                "hs_date_entered_poetry": 9999,
            },
        ),
    ],
    ids=[
        "Transforms stream schema/properties dictionary",
        "Transforms record w/ flat properties",
        "Transform record w/ nested properties",
        "Does not transform record w/o need to transformation",
        "Does not overwrite value for legacy field if legacy field exists",
    ],
)
def test_new_to_legacy_field_transformation(input, expected):
    transformer = NewtoLegacyFieldTransformation(DEALS_NEW_TO_LEGACY_FIELDS_MAPPING)
    transformer.transform(input)
    assert input == expected
