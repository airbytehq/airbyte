#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

from unittest.mock import Mock, patch

import pytest
import requests
from requests import Response

from airbyte_cdk.sources.declarative.retrievers import SimpleRetriever


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
def test_new_to_legacy_field_transformation(input, expected, components_module):
    deals_new_to_legacy_mapping = {
        "hs_date_entered_": "hs_v2_date_entered_",
        "hs_date_exited_": "hs_v2_date_exited_",
        "hs_time_in_": "hs_v2_latest_time_in_",
    }
    transformer = components_module.NewtoLegacyFieldTransformation(deals_new_to_legacy_mapping)
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
def test_migrate_empty_string_state(config, state, expected_should_migrate, expected_state, components_module):
    state_migration = components_module.MigrateEmptyStringState("updatedAt", config)

    actual_should_migrate = state_migration.should_migrate(stream_state=state)
    assert actual_should_migrate is expected_should_migrate

    if actual_should_migrate:
        assert state_migration.migrate(stream_state=state) == expected_state


def test_hubspot_rename_properties_transformation(components_module):
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
    transformation = components_module.HubspotRenamePropertiesTransformation()

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


def test_property_history_extractor(components_module):
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

    extractor = components_module.HubspotPropertyHistoryExtractor(
        field_path=["results"], entity_primary_key="dealId", additional_keys=["archived"], decoder=decoder, config={}, parameters={}
    )

    actual_records = list(extractor.extract_records(response=requests.Response()))

    assert actual_records == expected_records


def test_property_history_extractor_ignore_hs_lastmodifieddate(components_module):
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

    extractor = components_module.HubspotPropertyHistoryExtractor(
        field_path=["results"], entity_primary_key="dealId", additional_keys=[], decoder=decoder, config={}, parameters={}
    )

    actual_records = list(extractor.extract_records(response=requests.Response()))

    assert actual_records == expected_records


def test_flatten_associations_transformation(components_module):
    expected_record = {"id": "a2b", "Contacts": [101, 102], "Companies": [202, 209]}

    transformation = components_module.HubspotFlattenAssociationsTransformation()

    current_record = {
        "id": "a2b",
        "associations": {
            "Contacts": {"results": [{"id": 101}, {"id": 102}]},
            "Companies": {"results": [{"id": 202}, {"id": 209}]},
        },
    }

    transformation.transform(record=current_record, config={}, stream_state=None, stream_slice=None)

    assert current_record == expected_record


def test_associations_extractor(config, components_module):
    expected_records = [
        {"id": "123", "companies": ["909", "424"], "contacts": ["408"]},
        {
            "id": "456",
            "companies": ["606", "510"],
            "contacts": ["888"],
        },
    ]

    decoder = Mock()
    decoder.decode.return_value = [
        {
            "total": 2,
            "results": [{"id": "123", "updatedAt": "2025-05-01T00:00:00.000Z"}, {"id": "456", "updatedAt": "2025-05-01T00:00:00.000Z"}],
        }
    ]

    companies_mocked_associations_records = [
        {
            "from": {"id": "123"},
            "to": [{"associationTypes": [{"category": "HUBSPOT_DEFINED", "label": None, "typeId": 3}], "toObjectId": 909}],
        },
        {
            "from": {"id": "456"},
            "to": [{"associationTypes": [{"category": "HUBSPOT_DEFINED", "label": None, "typeId": 3}], "toObjectId": 606}],
        },
        {
            "from": {"id": "123"},
            "to": [{"associationTypes": [{"category": "HUBSPOT_DEFINED", "label": None, "typeId": 3}], "toObjectId": 424}],
        },
        {
            "from": {"id": "456"},
            "to": [{"associationTypes": [{"category": "HUBSPOT_DEFINED", "label": None, "typeId": 3}], "toObjectId": 510}],
        },
    ]

    contacts_mocked_associations_records = [
        {
            "from": {"id": "123"},
            "to": [{"associationTypes": [{"category": "HUBSPOT_DEFINED", "label": None, "typeId": 3}], "toObjectId": 408}],
        },
        {
            "from": {"id": "456"},
            "to": [{"associationTypes": [{"category": "HUBSPOT_DEFINED", "label": None, "typeId": 3}], "toObjectId": 888}],
        },
    ]

    extractor = components_module.HubspotAssociationsExtractor(
        field_path=["results"],
        entity="deals",
        associations_list=["companies", "contacts"],
        decoder=decoder,
        config=config,
        parameters={},
    )

    with patch.object(
        SimpleRetriever, "read_records", side_effect=[companies_mocked_associations_records, contacts_mocked_associations_records]
    ):
        records = list(extractor.extract_records(response=Response()))

        assert len(records) == 2
        assert records[0]["id"] == expected_records[0]["id"]
        assert records[0]["companies"] == expected_records[0]["companies"]
        assert records[0]["contacts"] == expected_records[0]["contacts"]

        assert records[1]["id"] == expected_records[1]["id"]
        assert records[1]["companies"] == expected_records[1]["companies"]
        assert records[1]["contacts"] == expected_records[1]["contacts"]


def test_extractor_supports_entity_interpolation(config, components_module):
    parameters = {"entity": "engagements_emails"}

    extractor = components_module.HubspotAssociationsExtractor(
        field_path=["results"],
        entity="{{ parameters['entity'] }}",
        associations_list=["companies", "contacts"],
        config=config,
        parameters=parameters,
    )

    entity = extractor._entity.eval(config=config)

    assert entity == "engagements_emails"


@pytest.mark.parametrize(
    "associations_list_value",
    [
        pytest.param(["contacts", "deals", "tickets"], id="test_static_associations"),
        pytest.param("{{ parameters['associations'] }}", id="test_interpolated_associations"),
    ],
)
def test_extractor_supports_associations_list_interpolation(config, associations_list_value, components_module):
    extractor = components_module.HubspotAssociationsExtractor(
        field_path=["results"],
        entity="emails",
        associations_list=associations_list_value,
        config=config,
        parameters={
            "associations": ["contacts", "deals", "tickets"],
        },
    )

    if isinstance(associations_list_value, str):
        evaluated_associations_list = extractor._associations_list.eval(config=config)
    else:
        evaluated_associations_list = extractor._associations_list

    assert evaluated_associations_list == ["contacts", "deals", "tickets"]


@pytest.mark.parametrize(
    "original_value,field_schema,expected_value",
    [
        pytest.param("", {"type": ["null", "number"]}, None, id="test_empty_string_is_none_for_non_string_types"),
        pytest.param(
            "1748246523456",
            {"type": ["null", "date-time"], "format": "date-time"},
            "2025-05-26T08:02:03+00:00",
            id="test_convert_millisecond_timestamp_to_seconds",
        ),
        pytest.param(
            "1748246523456.0",
            {"type": ["null", "date-time"], "format": "date-time"},
            "2025-05-26T08:02:03+00:00",
            id="test_overflow_error_float_returns_correct_date_time",
        ),
        pytest.param(
            "174824652345600.0",
            {"type": ["null", "date-time"], "format": "date-time"},
            "174824652345600.0",
            id="test_unparsable_overflow_error_returns_original_value",
        ),
    ],
)
def test_entity_schema_normalization(components_module, original_value, field_schema, expected_value):
    entity_schema_normalization = components_module.EntitySchemaNormalization()

    transform_function = entity_schema_normalization.get_transform_function()

    normalized_value = transform_function(original_value=original_value, field_schema=field_schema)

    assert normalized_value == expected_value


@pytest.mark.parametrize(
    "json_response,last_page_size,last_record,last_page_token_value,expected_next_page_token",
    [
        pytest.param(
            {"paging": {"next": {"after": 1200}}}, 200, {"id": 5000}, {"after": 1000}, {"after": 1200}, id="test_next_page_on_first_chunk"
        ),
        pytest.param(
            {"paging": {"next": {"after": 1200}}},
            100,
            {"id": 5000},
            {"after": 1000},
            None,
            id="test_stop_paging_when_last_page_is_less_than_page_size",
        ),
        pytest.param(
            {"paging": {"next": {"after": 1200}}}, 0, {"id": 5000}, {"after": 1000}, None, id="test_stop_paging_when_last_page_size_is_zero"
        ),
        pytest.param({}, 200, {"id": 5000}, {"after": 1000}, None, id="test_stop_paging_when_no_after_in_response"),
        pytest.param(
            {"paging": {"next": {"after": 10000}}},
            200,
            {"id": 25000},
            {"after": 9800},
            {"after": 0, "id": 25001},
            id="test_reset_page_and_move_to_next_chunk",
        ),
        pytest.param(
            {"paging": {"next": {"after": 200}}},
            200,
            {"id": 30000},
            {"after": 0, "id": 25001},
            {"after": 200, "id": 25001},
            id="test_next_page_on_next_chunk_of_records",
        ),
    ],
)
def test_crm_search_pagination_strategy(
    components_module, json_response, last_page_size, last_record, last_page_token_value, expected_next_page_token
):
    pagination_strategy = components_module.HubspotCRMSearchPaginationStrategy(page_size=200)

    response = Mock()
    response.json.return_value = json_response

    actual_next_page_token = pagination_strategy.next_page_token(
        response=response,
        last_page_size=last_page_size,
        last_record=last_record,
        last_page_token_value=last_page_token_value,
    )

    assert actual_next_page_token == expected_next_page_token
