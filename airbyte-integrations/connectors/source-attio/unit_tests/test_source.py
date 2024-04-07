#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

from airbyte_cdk.models import AirbyteCatalog
from source_attio.source import SourceAttio

WORKSPACE_ID = "70b4d96b-8410-4a24-bedf-64499605680e"


def test_check_connection_ok(requests_mock):
    requests_mock.get("https://api.attio.com/v2/self", json={"active": True, "scope": []})

    source = SourceAttio()
    logger_mock, config_mock = MagicMock(), MagicMock()
    ok, err = source.check_connection(logger_mock, config_mock)

    assert ok
    assert not err


def test_check_connection_unauthorized(requests_mock):
    requests_mock.get("https://api.attio.com/v2/self", json={"active": False})

    source = SourceAttio()
    logger_mock, config_mock = MagicMock(), MagicMock()
    ok, err = source.check_connection(logger_mock, config_mock)

    assert not ok
    assert err is not None
    assert str(err) == "Connection is inactive"


def test_discover(requests_mock, make_attribute_response, make_object_response):
    person_id = "876e432f-2aee-4d28-b02b-fc9a1f1f9b04"
    person_object = make_object_response(
        workspace_id=WORKSPACE_ID, api_slug="people", object_id=person_id, singular_noun="person", plural_noun="people"
    )
    person_attributes = [
        make_attribute_response(
            title="Email addresses",
            api_slug="email_addresses",
            type="email-address",
            is_multi=True,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Name",
            api_slug="name",
            type="personal-name",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Company",
            api_slug="company",
            type="record-reference",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
            allowed_object_ids=["c9cad75a-82f8-40c6-9edc-f567efdc2b9a"],
        ),
        make_attribute_response(
            title="Single Record",
            api_slug="single_record",
            type="record-reference",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
            allowed_object_ids=["c9cad75a-82f8-40c6-9edc-f567efdc2b9a", "3497d03e-bd8a-4a3f-a41f-f4705777e341"],
        ),
        make_attribute_response(
            title="Multi Record",
            api_slug="multi_record",
            type="record-reference",
            is_multi=True,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
            allowed_object_ids=["c9cad75a-82f8-40c6-9edc-f567efdc2b9a", "3497d03e-bd8a-4a3f-a41f-f4705777e341"],
        ),
        make_attribute_response(
            title="Description",
            api_slug="description",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Job title",
            api_slug="job_title",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Phone numbers",
            api_slug="phone_numbers",
            type="phone-number",
            is_multi=True,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Primary location",
            api_slug="primary_location",
            type="location",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="AngelList",
            api_slug="angellist",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Facebook",
            api_slug="facebook",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Instagram",
            api_slug="instagram",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="LinkedIn",
            api_slug="linkedin",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Twitter",
            api_slug="twitter",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="First calendar interaction",
            api_slug="first_calendar_interaction",
            type="interaction",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Strongest connection user",
            api_slug="strongest_connection_user",
            type="actor-reference",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Created at",
            api_slug="created_at",
            type="timestamp",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
        make_attribute_response(
            title="Created by",
            api_slug="created_by",
            type="actor-reference",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=person_id,
        ),
    ]

    company_id = "973cd405-102e-4409-9220-dd815951ffd6"
    company_object = make_object_response(
        workspace_id=WORKSPACE_ID, api_slug="companies", object_id=company_id, singular_noun="company", plural_noun="companies"
    )
    company_attributes = [
        make_attribute_response(
            title="Domains",
            api_slug="domains",
            type="domain",
            is_multi=True,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Name",
            api_slug="name",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Description",
            api_slug="description",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Team",
            api_slug="team",
            type="record-reference",
            is_multi=True,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
            allowed_object_ids=["c9cad75a-82f8-40c6-9edc-f567efdc2b9a"],
        ),
        make_attribute_response(
            title="Categories",
            api_slug="categories",
            type="select",
            is_multi=True,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Primary Location",
            api_slug="primary_location",
            type="location",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Logo URL",
            api_slug="logo_url",
            type="text",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Twitter Follower Count",
            api_slug="twitter_follower_count",
            type="number",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Estimated ARR USD",
            api_slug="estimated_arr_usd",
            type="select",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Funding Raised USD",
            api_slug="funding_raised_usd",
            type="currency",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="First Calendar Interaction",
            api_slug="first_calendar_interaction",
            type="interaction",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Created at",
            api_slug="created_at",
            type="timestamp",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
        make_attribute_response(
            title="Created by",
            api_slug="created_by",
            type="actor-reference",
            is_multi=False,
            workspace_id=WORKSPACE_ID,
            object_id=company_id,
        ),
    ]

    requests_mock.get(
        "https://api.attio.com/v2/objects",
        json={"data": [person_object, company_object]},
    )
    requests_mock.get(
        f"https://api.attio.com/v2/objects/{person_id}/attributes",
        json={"data": person_attributes},
    )
    requests_mock.get(
        f"https://api.attio.com/v2/objects/{company_id}/attributes",
        json={"data": company_attributes},
    )

    source = SourceAttio()
    logger_mock, config_mock = MagicMock(), MagicMock()
    airbyte_catalog = source.discover(logger_mock, config_mock)
    streams = airbyte_catalog.streams

    assert isinstance(airbyte_catalog, AirbyteCatalog)

    assert set([s.name for s in streams]) == set(
        [
            "workspace_members",
            "objects",
            "people",
            "people_attributes",
            "companies",
            "companies_attributes",
        ]
    )

    interaction_schema = {
        "type": ["object", "null"],
        "properties": {
            "interaction_type": {"type": "string"},
            "interacted_at": {"type": "string", "airbyte_type": "timestamp_with_timezone", "format": "date-time"},
            "owner_actor_type": {"type": ["string", "null"]},
            "owner_actor_id": {"type": ["string", "null"]},
        },
    }

    attribute_schemas = [s.json_schema for s in filter(lambda x: x.name in ["people_attributes", "companies_attributes"], streams)]
    for schema in attribute_schemas:
        expected_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "additionalProperties": True,
            "type": "object",
            "properties": {
                "workspace_id": {"type": "string"},
                "object_id": {"type": "string"},
                "attribute_id": {"type": "string"},
                "title": {"type": "string"},
                "description": {"type": ["string", "null"]},
                "api_slug": {"type": "string"},
                "type": {"type": "string"},
                "is_system_attribute": {"type": "boolean"},
                "is_writable": {"type": "boolean"},
                "is_required": {"type": "boolean"},
                "is_unique": {"type": "boolean"},
                "is_multiselect": {"type": "boolean"},
                "is_default_value_enabled": {"type": "boolean"},
                "is_archived": {"type": "boolean"},
                "default_value": {"type": ["string", "null"]},
                "relationship": {"type": ["string", "null"]},
                "config_record_reference_allowed_object_ids": {"type": ["array", "null"], "items": {"type": "string"}},
                "config_currency_display_type": {"type": ["string", "null"]},
                "config_currency_default_currency_code": {"type": ["string", "null"]},
                "created_at": {"type": "string"},
            },
        }
        assert schema == expected_schema

    person_stream = next(s for s in streams if s.name == "people")
    expected_person_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": True,
        "type": "object",
        "properties": {
            "workspace_id": {"type": "string"},
            "object_id": {"type": "string"},
            "record_id": {"type": "string"},
            "email_addresses": {
                "type": "array",
                "items": {"type": "string"},
            },
            "name_first_name": {"type": ["string", "null"]},
            "name_last_name": {"type": ["string", "null"]},
            "name_full_name": {"type": ["string", "null"]},
            # Return just the record ID for single value, single allow object attribute
            "company": {"type": ["string", "null"]},
            # For attributes with multiple allowed objects, return the object and the record ID
            "single_record": {
                "type": ["object", "null"],
                "properties": {
                    "target_object": {"type": "string"},
                    "target_record_id": {"type": "string"},
                },
            },
            # And return an array of that if we have a multiselect attribute
            "multi_record": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "target_object": {"type": "string"},
                        "target_record_id": {"type": "string"},
                    },
                },
            },
            "description": {"type": ["string", "null"]},
            "job_title": {"type": ["string", "null"]},
            "phone_numbers": {
                "type": "array",
                "items": {"type": "string"},
            },
            "primary_location_line_1": {"type": ["string", "null"]},
            "primary_location_line_2": {"type": ["string", "null"]},
            "primary_location_line_3": {"type": ["string", "null"]},
            "primary_location_line_4": {"type": ["string", "null"]},
            "primary_location_locality": {"type": ["string", "null"]},
            "primary_location_region": {"type": ["string", "null"]},
            "primary_location_postcode": {"type": ["string", "null"]},
            "primary_location_country_code": {"type": ["string", "null"]},
            "primary_location_longitude": {"type": ["string", "null"]},
            "primary_location_latitude": {"type": ["string", "null"]},
            "angellist": {"type": ["string", "null"]},
            "facebook": {"type": ["string", "null"]},
            "instagram": {"type": ["string", "null"]},
            "linkedin": {"type": ["string", "null"]},
            "twitter": {"type": ["string", "null"]},
            "first_calendar_interaction": interaction_schema,
            "strongest_connection_user": {
                "type": ["object", "null"],
                "properties": {
                    "referenced_actor_type": {"type": "string"},
                    "referenced_actor_id": {"type": "string"},
                },
            },
            "created_at": {"type": ["string", "null"], "airbyte_type": "timestamp_with_timezone", "format": "date-time"},
            "created_by": {
                "type": ["object", "null"],
                "properties": {
                    "referenced_actor_type": {"type": "string"},
                    "referenced_actor_id": {"type": "string"},
                },
            },
        },
    }
    assert person_stream.json_schema == expected_person_schema

    company_stream = next(s for s in streams if s.name == "companies")
    expected_company_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "additionalProperties": True,
        "type": "object",
        "properties": {
            "workspace_id": {"type": "string"},
            "object_id": {"type": "string"},
            "record_id": {"type": "string"},
            "domains": {
                "type": "array",
                "items": {"type": "string"},
            },
            "name": {"type": ["string", "null"]},
            "description": {"type": ["string", "null"]},
            "team": {
                "type": "array",
                "items": {
                    "type": "string",
                },
            },
            "categories": {
                "type": "array",
                "items": {"type": "string"},
            },
            "primary_location_line_1": {"type": ["string", "null"]},
            "primary_location_line_2": {"type": ["string", "null"]},
            "primary_location_line_3": {"type": ["string", "null"]},
            "primary_location_line_4": {"type": ["string", "null"]},
            "primary_location_locality": {"type": ["string", "null"]},
            "primary_location_region": {"type": ["string", "null"]},
            "primary_location_postcode": {"type": ["string", "null"]},
            "primary_location_country_code": {"type": ["string", "null"]},
            "primary_location_latitude": {"type": ["string", "null"]},
            "primary_location_longitude": {"type": ["string", "null"]},
            "logo_url": {"type": ["string", "null"]},
            "twitter_follower_count": {"type": ["number", "null"]},
            "estimated_arr_usd": {"type": ["string", "null"]},
            "funding_raised_usd": {"type": ["number", "null"]},
            "first_calendar_interaction": interaction_schema,
            "created_at": {"type": ["string", "null"], "airbyte_type": "timestamp_with_timezone", "format": "date-time"},
            "created_by": {
                "type": ["object", "null"],
                "properties": {
                    "referenced_actor_type": {"type": "string"},
                    "referenced_actor_id": {"type": "string"},
                },
            },
        },
    }
    assert company_stream.json_schema == expected_company_schema


def test_streams(requests_mock, make_object_response):
    person_object = make_object_response(workspace_id=WORKSPACE_ID, api_slug="people", singular_noun="person", plural_noun="people")
    company_object = make_object_response(workspace_id=WORKSPACE_ID, api_slug="companies", singular_noun="company", plural_noun="companies")
    user_object = make_object_response(workspace_id=WORKSPACE_ID, api_slug="users", singular_noun="user", plural_noun="users")
    custom_object = make_object_response(workspace_id=WORKSPACE_ID, api_slug="foo", singular_noun="foo", plural_noun="foos")
    objects = [person_object, company_object, user_object, custom_object]

    requests_mock.get("https://api.attio.com/v2/objects", json={"data": objects})

    source = SourceAttio()
    config_mock = MagicMock()
    streams = list(source.streams(config_mock))

    assert set([s.name for s in streams]) == set(
        [
            "workspace_members",
            "objects",
            "people",
            "people_attributes",
            "companies",
            "companies_attributes",
            "users",
            "users_attributes",
            "foo",
            "foo_attributes",
        ]
    )
