#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock

import pytest
import requests
from source_hubspot.components import HubspotRenamePropertiesTransformation, HubspotPropertyHistoryExtractor, MigrateEmptyStringState, NewtoLegacyFieldTransformation
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


@pytest.mark.parametrize(
    "state, expected_should_migrate, expected_state",
    [
        ({"updatedAt": ""}, True, {"updatedAt": "2021-01-10T00:00:00Z"}),
        ({"updatedAt": "2022-01-10T00:00:00Z"}, False, {"updatedAt": "2022-01-10T00:00:00Z"}),
    ],
    ids=[
        "Invalid state: empty string, should migrate",
        "Valid state: date string, no need to migrate",
    ],
)
def test_migrate_empty_string_state(config, state, expected_should_migrate, expected_state):
    state_migration = MigrateEmptyStringState("updatedAt", config)

    actual_should_migrate = state_migration.should_migrate(stream_state=state)
    assert actual_should_migrate is expected_should_migrate

    if actual_should_migrate:
        assert state_migration.migrate(stream_state=state) == expected_state


def test_hubspot_rename_properties_transformation():
    expected_properties = {
        "properties_amount": {"type": ["null", "number"]},
        "properties_hs_v2_date_entered_closedwon": {"format": "date-time", "type": ["null", "string"]},
        "properties_hs_v2_date_exited_closedlost": {"format": "date-time", "type": ["null", "string"]},
        "properties_hs_v2_latest_time_in_contractsent": {"format": "date-time", "type": ["null", "string"]},
        "properties": {
            "type": "object",
            "properties": {
                "amount": {"type": ["null", "number"]},
                "hs_v2_date_entered_closedwon": {"format": "date-time", "type": ["null", "string"]},
                "hs_v2_date_exited_closedlost": {"format": "date-time", "type": ["null", "string"]},
                "hs_v2_latest_time_in_contractsent": {"format": "date-time", "type": ["null", "string"]},
            },
        },
    }

    dynamic_properties_record = {
        "amount": {"type": ["null", "number"]},
        "hs_v2_date_entered_closedwon": {"format": "date-time", "type": ["null", "string"]},
        "hs_v2_date_exited_closedlost": {"format": "date-time", "type": ["null", "string"]},
        "hs_v2_latest_time_in_contractsent": {"format": "date-time", "type": ["null", "string"]},
    }
    transformation = HubspotRenamePropertiesTransformation()

    transformation.transform(record=dynamic_properties_record)

    assert dynamic_properties_record["properties_amount"] == expected_properties["properties_amount"]
    assert (
        dynamic_properties_record["properties_hs_v2_date_entered_closedwon"]
        == expected_properties["properties_hs_v2_date_entered_closedwon"]
    )
    assert (
        dynamic_properties_record["properties_hs_v2_date_exited_closedlost"]
        == expected_properties["properties_hs_v2_date_exited_closedlost"]
    )
    assert (
        dynamic_properties_record["properties_hs_v2_latest_time_in_contractsent"]
        == expected_properties["properties_hs_v2_latest_time_in_contractsent"]
    )
    assert dynamic_properties_record["properties"] == expected_properties["properties"]


def test_property_history_extractor():
    expected_records = [
        {
            "dealId": "1234",
            "property": "pilot",
            "sourceId": "0",
            "sourceType": "MIGRATION",
            "timestamp": "2022-08-04T15:57:22.188Z",
            "updatedByUserId": 987,
            "value": "rei_ayanami",
            "archived": False,
        },
        {
            "dealId": "1234",
            "property": "pilot",
            "sourceId": "1",
            "sourceType": "MIGRATION",
            "timestamp": "2022-08-04T15:57:22.188Z",
            "updatedByUserId": 987,
            "value": "shinji_ikari",
            "archived": False,
        },
        {
            "dealId": "1234",
            "property": "pilot",
            "sourceId": "2",
            "sourceType": "MIGRATION",
            "timestamp": "2022-08-04T15:57:22.188Z",
            "updatedByUserId": 987,
            "value": "asuka_langley_soryu",
            "archived": False,
        },
        {
            "dealId": "1234",
            "property": "evangelion_unit",
            "sourceId": "0",
            "sourceType": "MIGRATION",
            "timestamp": "2022-08-04T15:57:22.188Z",
            "updatedByUserId": 987,
            "value": "0",
            "archived": False,
        },
        {
            "dealId": "1234",
            "property": "evangelion_unit",
            "sourceId": "1",
            "sourceType": "MIGRATION",
            "timestamp": "2022-08-04T15:57:22.188Z",
            "updatedByUserId": 987,
            "value": "1",
            "archived": False,
        },
        {
            "dealId": "1234",
            "property": "evangelion_unit",
            "sourceId": "2",
            "sourceType": "MIGRATION",
            "timestamp": "2022-08-04T15:57:22.188Z",
            "updatedByUserId": 987,
            "value": "2",
            "archived": False,
        },
    ]

    response = [
        {
            "results": [
                {
                    "id": "1234",
                    "properties": {
                        "amount": "3",
                        "closedate": "2022-08-31T15:56:49.107Z",
                        "dealname": "Evangelion Contracts",
                        "dealstage": "completed",
                        "hs_lastmodifieddate": "2024-08-28T00:00:00.000Z",
                        "hs_object_id": "5678",
                        "pipeline": "default",
                    },
                    "propertiesWithHistory": {
                        "pilot": [
                            {
                                "value": "rei_ayanami",
                                "timestamp": "2022-08-04T15:57:22.188Z",
                                "sourceType": "MIGRATION",
                                "sourceId": "0",
                                "updatedByUserId": 987,
                            },
                            {
                                "value": "shinji_ikari",
                                "timestamp": "2022-08-04T15:57:22.188Z",
                                "sourceType": "MIGRATION",
                                "sourceId": "1",
                                "updatedByUserId": 987,
                            },
                            {
                                "value": "asuka_langley_soryu",
                                "timestamp": "2022-08-04T15:57:22.188Z",
                                "sourceType": "MIGRATION",
                                "sourceId": "2",
                                "updatedByUserId": 987,
                            },
                        ],
                        "evangelion_unit": [
                            {
                                "value": "0",
                                "timestamp": "2022-08-04T15:57:22.188Z",
                                "sourceType": "MIGRATION",
                                "sourceId": "0",
                                "updatedByUserId": 987,
                            },
                            {
                                "value": "1",
                                "timestamp": "2022-08-04T15:57:22.188Z",
                                "sourceType": "MIGRATION",
                                "sourceId": "1",
                                "updatedByUserId": 987,
                            },
                            {
                                "value": "2",
                                "timestamp": "2022-08-04T15:57:22.188Z",
                                "sourceType": "MIGRATION",
                                "sourceId": "2",
                                "updatedByUserId": 987,
                            },
                        ],
                    },
                    "archived": False,
                }
            ]
        }
    ]

    decoder = Mock()
    decoder.decode.return_value = response

    extractor = HubspotPropertyHistoryExtractor(
        field_path=["results"], entity_primary_key="dealId", additional_keys=["archived"], decoder=decoder, config={}, parameters={}
    )

    actual_records = list(extractor.extract_records(response=requests.Response()))

    assert actual_records == expected_records


def test_property_history_extractor_ignore_hs_lastmodifieddate():
    expected_records = [
        {
            "dealId": "1234",
            "property": "pilot",
            "sourceId": "0",
            "sourceType": "MIGRATION",
            "timestamp": "2022-08-04T15:57:22.188Z",
            "updatedByUserId": 987,
            "value": "rei_ayanami",
        }
    ]

    response = [
        {
            "results": [
                {
                    "id": "1234",
                    "properties": {
                        "amount": "3",
                        "closedate": "2022-08-31T15:56:49.107Z",
                        "dealname": "Evangelion Contracts",
                        "dealstage": "completed",
                        "hs_lastmodifieddate": "2024-08-28T00:00:00.000Z",
                        "hs_object_id": "5678",
                        "pipeline": "default",
                    },
                    "propertiesWithHistory": {
                        "pilot": [
                            {
                                "value": "rei_ayanami",
                                "timestamp": "2022-08-04T15:57:22.188Z",
                                "sourceType": "MIGRATION",
                                "sourceId": "0",
                                "updatedByUserId": 987,
                            },
                        ],
                        "hs_lastmodifieddate": [
                            {
                                "value": "2022-08-04T15:57:22.188Z",
                                "timestamp": "2022-08-04T15:57:22.188Z",
                                "sourceType": "MIGRATION",
                                "sourceId": "0",
                                "updatedByUserId": 987,
                            },
                        ],
                    },
                }
            ]
        }
    ]

    decoder = Mock()
    decoder.decode.return_value = response

    extractor = HubspotPropertyHistoryExtractor(
        field_path=["results"], entity_primary_key="dealId", additional_keys=[], decoder=decoder, config={}, parameters={}
    )

    actual_records = list(extractor.extract_records(response=requests.Response()))

    assert actual_records == expected_records
