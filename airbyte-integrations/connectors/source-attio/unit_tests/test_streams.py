#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock
from uuid import uuid4
from airbyte_cdk.models import SyncMode
import requests

import pytest
from source_attio.source import (
    AttioStream,
    WorkspaceMembers,
    Objects,
    ObjectAttributes,
    Records,
)

WORKSPACE_ID =  "1eb8b8be-2b16-4795-81d8-6cd004812f92"

@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(AttioStream, "primary_key", "test_primary_key")
    mocker.patch.object(AttioStream, "__abstractmethods__", set())


def test_request_headers(patch_base_class):
    stream = AttioStream()
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {
        # Auth handled by HttpAuthenticator
        "Content-Type": "application/json"
    }
    assert stream.request_headers(**inputs) == expected_headers


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = AttioStream()
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = AttioStream()
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


@pytest.mark.parametrize(
    ("response_data", "expected"),
    [
        ([], []),
        (
            [
                {
                    "id": {
                        "workspace_id": WORKSPACE_ID ,
                        "workspace_member_id": "08234bc6-c733-464c-b46f-11ae114aa3cc",
                    },
                    "first_name": "Alice",
                    "last_name": "Adams",
                    "avatar_url": "https://assets.attio.com/avatars/1f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "alice@example.com",
                    "access_level": "admin",
                    "created_at": "2020-03-13T23:20:19.285000000Z",
                }
            ],
            [
                {
                    "workspace_id": WORKSPACE_ID ,
                    "workspace_member_id": "08234bc6-c733-464c-b46f-11ae114aa3cc",
                    "first_name": "Alice",
                    "last_name": "Adams",
                    "avatar_url": "https://assets.attio.com/avatars/1f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "alice@example.com",
                    "access_level": "admin",
                    "created_at": "2020-03-13T23:20:19.285000000Z",
                }
            ],
        ),
        (
            [
                {
                    "id": {
                        "workspace_id": WORKSPACE_ID ,
                        "workspace_member_id": "08234bc6-c733-464c-b46f-11ae114aa3cc",
                    },
                    "first_name": "Alice",
                    "last_name": "Adams",
                    "avatar_url": "https://assets.attio.com/avatars/1f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "alice@example.com",
                    "access_level": "admin",
                    "created_at": "2020-03-13T23:20:19.285000000Z",
                },
                {
                    "id": {
                        "workspace_id": WORKSPACE_ID ,
                        "workspace_member_id": "26e027da-fcc7-4a47-b784-8c6cb93476e5",
                    },
                    "first_name": "Bob",
                    "last_name": "Booley",
                    "avatar_url": "https://assets.attio.com/avatars/2f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "bob@example.com",
                    "access_level": "admin",
                    "created_at": "2023-03-13T23:20:19.285000000Z",
                },
            ],
            [
                {
                    "workspace_id": WORKSPACE_ID ,
                    "workspace_member_id": "08234bc6-c733-464c-b46f-11ae114aa3cc",
                    "first_name": "Alice",
                    "last_name": "Adams",
                    "avatar_url": "https://assets.attio.com/avatars/1f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "alice@example.com",
                    "access_level": "admin",
                    "created_at": "2020-03-13T23:20:19.285000000Z",
                },
                {
                    "workspace_id": WORKSPACE_ID ,
                    "workspace_member_id": "26e027da-fcc7-4a47-b784-8c6cb93476e5",
                    "first_name": "Bob",
                    "last_name": "Booley",
                    "avatar_url": "https://assets.attio.com/avatars/2f3l035b-fe59-4b2c-b4c9-b95e1d437e5d?etag=1182392508604",
                    "email_address": "bob@example.com",
                    "access_level": "admin",
                    "created_at": "2023-03-13T23:20:19.285000000Z",
                },
            ],
        ),
    ],
)
def test_workspace_member_parse(response_data, expected):
    stream = WorkspaceMembers()
    response = MagicMock()
    response.json.return_value = {"data": response_data}
    inputs = {"response": response, "stream_slice": None, "stream_state": None, "next_page_token": None}
    parsed = stream.parse_response(**inputs)
    assert parsed == expected

def test_objects_parse(make_object_response):
    stream = Objects()
    response = MagicMock()
    person_id = "afe2011a-1169-44df-8228-8bec85061a3a"
    person_response = make_object_response(
        workspace_id=WORKSPACE_ID, api_slug="people", singular_noun="person", plural_noun="people", object_id=person_id,
    )
    response.json.return_value = {"data": [person_response]}
    inputs = {"response": response, "stream_slice": None, "stream_state": None, "next_page_token": None}
    parsed = stream.parse_response(**inputs)

    assert len(parsed) == 1
    parsed_person = parsed[0]
    assert parsed_person["workspace_id"] == WORKSPACE_ID
    assert parsed_person["object_id"] == person_id
    assert parsed_person["singular_noun"] == "person"
    assert parsed_person["plural_noun"] == "people"
    assert parsed_person["api_slug"] == "people"
    assert isinstance(parsed_person["created_at"], str)

def test_attributes_pagination(requests_mock, make_attribute_response):
    object_id = str(uuid4())
    object_slug = "my_slug"
    limit = 5

    base_attr = {"workspace_id": WORKSPACE_ID, "object_id": object_id}
    num_attributes = (limit * 2) - 1
    attributes = [make_attribute_response(type="text", is_multi=False, **base_attr) for _ in range(num_attributes)]

    requests_mock.get(
        f"https://api.attio.com/v2/objects/{object_id}/attributes",
        [
            {"json": {"data": attributes[:limit]}, "status_code": 200},
            {"json": {"data": attributes[limit:]}, "status_code": 200},
        ]
    )

    attributes_stream = ObjectAttributes(object_slug=object_slug, object_id=object_id, limit=limit)
    attributes_read = list(attributes_stream.read_records(sync_mode=SyncMode.full_refresh))

    assert len(attributes_read) == num_attributes

def test_attributes_parse_response(make_attribute_response):
    object_id = "acf2060b-2d82-491f-ba9f-2ed4465f154c"
    object_slug = "foo_object"
    attribute_id = "acf2060b-2d82-491f-ba9f-2ed4465f154c"
    api_slug = "foo_attribute"

    stream = ObjectAttributes(
        object_id=object_id,
        object_slug=object_slug
    )
    response = MagicMock()
    response.json.return_value = {"data": [make_attribute_response(
        workspace_id=WORKSPACE_ID,
        object_id=object_id,
        type="text",
        attribute_id=attribute_id,
        is_multi=False,
        api_slug=api_slug
    )]}
    inputs = {"response": response, "stream_slice": None, "stream_state": None, "next_page_token": None}
    parsed = stream.parse_response(**inputs)

    assert len(parsed) == 1
    attribute = parsed[0]
    assert attribute["workspace_id"] == WORKSPACE_ID
    assert attribute["object_id"] == object_id
    assert attribute["attribute_id"] == attribute_id
    assert attribute["api_slug"] == api_slug
    assert isinstance(attribute["title"], str)
    assert isinstance(attribute["description"], str)
    assert attribute["type"] == "text"
    assert attribute["is_multiselect"] == False
    assert isinstance(attribute["is_system_attribute"], bool)
    assert isinstance(attribute["is_writable"], bool)
    assert isinstance(attribute["is_required"], bool)
    assert isinstance(attribute["is_unique"], bool)
    assert isinstance(attribute["is_archived"], bool)
    assert attribute["default_value"] is None
    assert attribute["is_default_value_enabled"] is False
    assert attribute["relationship"] is None
    assert attribute["config_record_reference_allowed_object_ids"] is None
    assert attribute["config_currency_display_type"] is None
    assert attribute["config_currency_default_currency_code"] is None
    assert isinstance(attribute["created_at"], str)

def test_records_parse_response(requests_mock, make_attribute_response, make_record_response):
    object_slug = "foo_slug"
    object_id = "93c2beaa-c867-494b-bbe5-7ee997952d04"
    base_attr = {"workspace_id": WORKSPACE_ID, "object_id": object_id}

    attributes = [
        make_attribute_response(api_slug="text_single", type="text", is_multi=False, **base_attr),
        make_attribute_response(api_slug="number_single", type="number", is_multi=False, **base_attr),
        make_attribute_response(api_slug="checkbox_single", type="checkbox", is_multi=False, **base_attr),
        make_attribute_response(api_slug="currency_single", type="currency", is_multi=False, **base_attr),
        make_attribute_response(api_slug="date_single", type="date", is_multi=False, **base_attr),
        make_attribute_response(api_slug="timestamp_single", type="timestamp", is_multi=False, **base_attr),
        make_attribute_response(api_slug="rating_single", type="rating", is_multi=False, **base_attr),
        make_attribute_response(api_slug="status_single", type="status", is_multi=False, **base_attr),
        make_attribute_response(api_slug="select_single", type="select", is_multi=False, **base_attr),
        make_attribute_response(api_slug="select_multi", type="select", is_multi=True, **base_attr),
        make_attribute_response(api_slug="record_reference_single", type="record-reference", is_multi=False, **base_attr),
        make_attribute_response(api_slug="record_reference_multi", type="record-reference", is_multi=True, **base_attr),
        make_attribute_response(api_slug="record_reference_single_allowed_single", type="record-reference", is_multi=False, allowed_object_ids=["c5a593c1-7732-4c05-9d03-a9c2a2f289d6"], **base_attr),
        make_attribute_response(api_slug="record_reference_single_allowed_multi", type="record-reference", is_multi=True, allowed_object_ids=["c5a593c1-7732-4c05-9d03-a9c2a2f289d6"], **base_attr),
        make_attribute_response(api_slug="actor_reference_single", type="actor-reference", is_multi=False, **base_attr),
        make_attribute_response(api_slug="actor_reference_multi", type="actor-reference", is_multi=True, **base_attr),
        make_attribute_response(api_slug="location_single", type="location", is_multi=False, **base_attr),
        make_attribute_response(api_slug="domain_multi", type="domain", is_multi=True, **base_attr),
        make_attribute_response(api_slug="email_address_multi", type="email-address", is_multi=True, **base_attr),
        make_attribute_response(api_slug="phone_number_multi", type="phone-number", is_multi=True, **base_attr),
        make_attribute_response(api_slug="interaction_single", type="interaction", is_multi=True, **base_attr),
        make_attribute_response(api_slug="interaction_multi", type="interaction", is_multi=True, **base_attr),
        make_attribute_response(api_slug="personal_name", type="personal-name", is_multi=False, **base_attr)
    ]

    requests_mock.get(f"https://api.attio.com/v2/objects/{object_id}/attributes", json={"data": attributes})

    stream = Records(
        object_id=object_id,
        object_slug=object_slug
    )
    response = MagicMock()
    record_id = "2ebc603c-f2ce-476d-8fb7-26cc0f0a81a8"
    values = {
        "text_single": [
            {
                "value": "foo",
                "attribute_type": "text",
            }
        ],
        "number_single": [
            {
                "value": 123,
                "attribute_type": "number"
            }
        ],
        "checkbox_single": [
            {
                "value": True,
                "attribute_type": "checkbox"
            }
        ],
        "currency_single": [
            {
                "currency_value": 12.12,
                "currency_code": "USD",
                "attribute_type": "currency"
            },
        ],
        "date_single": [
            {
                "value": "2022-01-01",
                "attribute_type": "date"
            }
        ],
        "timestamp_single": [
            {
                "value": "2022-01-01T00:00:00Z",
                "attribute_type": "timestamp"
            }
        ],
        "rating_single": [
            {
                "value": 3,
                "attribute_type": "rating"
            }
        ],
        "status_single": [
            {
                "status": {
                    "id": {
                        "workspace_id": WORKSPACE_ID,
                        "attribute_id": "4cb29568-9f61-4e01-beaf-bb703c34355a",
                        "object_id": object_id,
                        "status_id": "47357af0-2004-46a7-8116-ab95fb4000a7",
                    },
                    "title": "A",
                    "is_archived": False,
                    "celebration_enabled": False,
                    "target_time_in_status": None,
                },
                "attribute_type": "status",
            }
        ],
        "select_single": [
            {
                "option": {
                    "id": {
                        "workspace_id": WORKSPACE_ID,
                        "attribute_id": "58cca11d-e020-404d-9d8e-f07376874965",
                        "object_id": object_id,
                        "option_id": "430441fb-106b-4b6f-90aa-545fcfa63e52",
                    },
                    "title": "A",
                    "is_archived": False,
                },
                "attribute_type": "select"
            }
        ],
        "select_multi": [
            {
                "option": {
                    "id": {
                        "workspace_id": WORKSPACE_ID,
                        "attribute_id": "89d3e91c-ea9f-41df-a484-0c7efdbfbb05",
                        "object_id": object_id,
                        "option_id": "bc271137-e056-4c67-9dfa-a8ef3083a4d0",
                    },
                    "title": "A",
                    "is_archived": False,
                },
                "attribute_type": "select"
            },
            {
                "option": {
                    "id": {
                        "workspace_id": WORKSPACE_ID,
                        "attribute_id": "89d3e91c-ea9f-41df-a484-0c7efdbfbb05",
                        "object_id": object_id,
                        "option_id": "9e965662-1b44-41f6-a896-fef33cbf4061",
                    },
                    "title": "B",
                    "is_archived": False,
                },
                "attribute_type": "select"
            },
        ],
        "record_reference_single": [
            {
                "target_object": "people",
                "target_record_id": "ec08c6df-5eeb-40cb-b84a-054086f5301f",
                "attribute_type": "record-reference"
            }
        ],
        "record_reference_multi": [
            {
                "target_object": "people",
                "target_record_id": "ec08c6df-5eeb-40cb-b84a-054086f5301f",
                "attribute_type": "record-reference"
            },
            {
                "target_object": "people",
                "target_record_id": "fab0ce74-a063-41cd-a65a-661006611c30",
                "attribute_type": "record-reference"
            }
        ],
        "record_reference_single_allowed_single": [
            {
                "target_object": "people",
                "target_record_id": "61ac43d6-2cd6-437c-a4c0-533c502f1bf5",
                "attribute_type": "record-reference"
            }
        ],
        "record_reference_single_allowed_multi": [
            {
                "target_object": "people",
                "target_record_id": "61ac43d6-2cd6-437c-a4c0-533c502f1bf5",
                "attribute_type": "record-reference"
            },
            {
                "target_object": "people",
                "target_record_id": "042a79b2-0a99-41b8-9673-e7240af60b63",
                "attribute_type": "record-reference"
            }
        ],
        "actor_reference_single": [
            {
                "referenced_actor_id": "0a3cc283-97bb-4393-b1cf-f0c21de294f6",
                "referenced_actor_type": "workspace-member",
                "attribute_type": "actor-reference"
            }
        ],
        "actor_reference_multi": [
            {
                "referenced_actor_id": "0a3cc283-97bb-4393-b1cf-f0c21de294f6",
                "referenced_actor_type": "workspace-member",
                "attribute_type": "actor-reference"
            },
            {
                "referenced_actor_id": "944647dd-1150-46ec-950d-6791be5a57aa",
                "referenced_actor_type": "workspace-member",
                "attribute_type": "actor-reference"
            }
        ],
        "location_single": [
            {
                "attribute_type": "location",
                "line_1": "123 Fake St",
                "line_2": "Apt 1",
                "line_3": "Floor 2",
                "line_4": "Suite 3",
                "locality": "San Francisco",
                "region": "CA",
                "postcode": "94107",
                "country_code": "US",
                "longitude": "-122.4006",
                "latitude": "37.7908",
            }
        ],
        "domain_multi": [
            {
                "domain": "app.attio.com",
                "root_domain": "attio.com",
                "attribute_type": "domain"
            },
            {
                "domain": "maps.google.com",
                "root_domain": "google.com",
                "attribute_type": "domain"
            }
        ],
        "email_address_multi": [
            {
                "original_email_address": "alice@sub.example.com",
                "email_address": "alice@sub.example.com",
                "email_domain": "sub.example.com",
                "email_root_domain": "example.com",
                "email_local_specifier": "alice",
                "attribute_type": "email-address"
            },
            {
                "original_email_address": "bob@sub.example.com",
                "email_address": "bob@sub.example.com",
                "email_domain": "sub.example.com",
                "email_root_domain": "example.com",
                "email_local_specifier": "bob",
                "attribute_type": "email-address"
            },
        ],
        "phone_number_multi": [
            {
                "phone_number": "+14155552671",
                "country_code": "US",
                "original_phone_number": "+14155552671",
                "attribute_type": "phone-number"
            },
            {
                "phone_number": "+14155552672",
                "country_code": "US",
                "original_phone_number": "+14155552672",
                "attribute_type": "phone-number"
            }
        ],
        "interaction_single": [{
            "interaction_type": "email",
            "interacted_at": "2022-01-01T00:00:00Z",
            "owner_actor": {
                "id": "0a3cc283-97bb-4393-b1cf-f0c21de294f6",
                "type": "workspace-member"
            },
            "attribute_type": "interaction",
        }],
        "interaction_multi": [{
            "interaction_type": "email",
            "interacted_at": "2022-01-01T00:00:00Z",
            "owner_actor": {
                "id": "0a3cc283-97bb-4393-b1cf-f0c21de294f6",
                "type": "workspace-member"
            },
            "attribute_type": "interaction",
        }],
        "personal_name": [
            {
                "first_name": "Alice",
                "last_name": "Smith",
                "full_name": "Alice Smith",
                "attribute_type": "personal-name"
            }
        ]
    }

    response.json.return_value = {"data": [make_record_response(
        workspace_id=WORKSPACE_ID,
        object_id=object_id,
        record_id=record_id,
        values=values,
    )]}
    inputs = {"response": response, "stream_slice": None, "stream_state": None, "next_page_token": None}
    parsed = list(stream.parse_response(**inputs))

    assert len(parsed) == 1
    record = parsed[0]
    assert record["workspace_id"] == WORKSPACE_ID
    assert record["object_id"] == object_id
    assert record["record_id"] == record_id
    assert isinstance(record["created_at"], str)

    # Assert specific values
    assert record["text_single"] == "foo"
    assert record["number_single"] == 123
    assert record["checkbox_single"] == True
    assert record["currency_single"] == 12.12
    assert record["date_single"] == "2022-01-01"
    assert record["timestamp_single"] == "2022-01-01T00:00:00Z"
    assert record["rating_single"] == 3
    assert record["status_single"] == "A"
    assert record["select_single"] == "A"

    assert record["select_multi"][0] == "A"
    assert record["select_multi"][1] == "B"

    assert record["record_reference_single"]["target_object"] == "people"
    assert record["record_reference_single"]["target_record_id"] == "ec08c6df-5eeb-40cb-b84a-054086f5301f"

    assert record["record_reference_multi"][0]["target_object"] == "people"
    assert record["record_reference_multi"][0]["target_record_id"] == "ec08c6df-5eeb-40cb-b84a-054086f5301f"
    assert record["record_reference_multi"][1]["target_object"] == "people"
    assert record["record_reference_multi"][1]["target_record_id"] == "fab0ce74-a063-41cd-a65a-661006611c30"

    assert record["record_reference_single_allowed_single"] == "61ac43d6-2cd6-437c-a4c0-533c502f1bf5"

    assert record["record_reference_single_allowed_multi"] == ["61ac43d6-2cd6-437c-a4c0-533c502f1bf5", "042a79b2-0a99-41b8-9673-e7240af60b63"]

    assert record["actor_reference_single"]["referenced_actor_type"] == "workspace-member"

    assert record["actor_reference_multi"][0]["referenced_actor_type"] == "workspace-member"
    assert record["actor_reference_multi"][0]["referenced_actor_id"] == "0a3cc283-97bb-4393-b1cf-f0c21de294f6"
    assert record["actor_reference_multi"][1]["referenced_actor_type"] == "workspace-member"
    assert record["actor_reference_multi"][1]["referenced_actor_id"] == "944647dd-1150-46ec-950d-6791be5a57aa"

    assert record["location_single_line_1"] == "123 Fake St"
    assert record["location_single_line_2"] == "Apt 1"
    assert record["location_single_line_3"] == "Floor 2"
    assert record["location_single_line_4"] == "Suite 3"
    assert record["location_single_locality"] == "San Francisco"
    assert record["location_single_region"] == "CA"
    assert record["location_single_postcode"] == "94107"
    assert record["location_single_country_code"] == "US"

    assert record["domain_multi"][0] == "app.attio.com"
    assert record["domain_multi"][1] == "maps.google.com"

    assert record["email_address_multi"][0] == "alice@sub.example.com"
    assert record["email_address_multi"][1] == "bob@sub.example.com"

    assert record["phone_number_multi"][0] == "+14155552671"
    assert record["phone_number_multi"][1] == "+14155552672"

    assert "interaction_single" not in record
    assert "interaction_multi" not in record

    assert record["personal_name_first_name"] == "Alice"
    assert record["personal_name_last_name"] == "Smith"
    assert record["personal_name_full_name"] == "Alice Smith"
   

def test_records_get_json_schema(requests_mock, make_attribute_response):
    object_slug = "my_slug"
    object_id = "806dfd50-f030-4b03-8281-ee5e77185b93"
    base_args = {"workspace_id": WORKSPACE_ID, "object_id": object_id}

    attributes = [
        make_attribute_response(type="text", is_multi=False, **base_args),
        make_attribute_response(type="number", is_multi=False, **base_args),
        make_attribute_response(type="checkbox", is_multi=False, **base_args),
        make_attribute_response(type="currency", is_multi=False, **base_args),
        make_attribute_response(type="date", is_multi=False, **base_args),
        make_attribute_response(type="timestamp", is_multi=False, **base_args),
        make_attribute_response(type="rating", is_multi=False, **base_args),
        make_attribute_response(type="status", is_multi=False, **base_args),
        make_attribute_response(type="select", is_multi=False, **base_args),
        make_attribute_response(type="select", is_multi=True, **base_args),
        make_attribute_response(type="record-reference", is_multi=False, **base_args),
        make_attribute_response(type="record-reference", is_multi=True, **base_args),
        make_attribute_response(type="actor-reference", is_multi=False, **base_args),
        make_attribute_response(type="actor-reference", is_multi=True, **base_args),
        make_attribute_response(type="location", is_multi=False, **base_args),
        make_attribute_response(type="domain", is_multi=True, **base_args),
        make_attribute_response(type="email-address", is_multi=True, **base_args),
        make_attribute_response(type="phone-number", is_multi=True, **base_args),
        make_attribute_response(type="interaction", is_multi=True, **base_args),
        make_attribute_response(type="interaction", is_multi=False, **base_args),
        make_attribute_response(type="personal-name", is_multi=False, **base_args)
    ]

    requests_mock.get(f"https://api.attio.com/v2/objects/{object_id}/attributes", json={"data": attributes})

    record_stream = Records(object_slug=object_slug, object_id=object_id)

    schema = record_stream.get_json_schema()
    assert schema["$schema"] == "http://json-schema.org/draft-07/schema#"
    assert schema["additionalProperties"] == True
    assert schema["type"] == "object"

    properties = schema["properties"]

    for attribute in attributes:
        t, slug, is_multi = attribute["type"], attribute["api_slug"], attribute["is_multiselect"]

        # assert that interaction attributes do not appear in the schema
        if t == "interaction":
            assert slug not in schema
            continue

        if t == "personal-name":
            # We break the names down into their sub fields
            assert properties[slug + "_first_name"] == {"type": ["string", "null"]}
            assert properties[slug + "_last_name"] == {"type": ["string", "null"]}
            assert properties[slug + "_full_name"] == {"type": ["string", "null"]}
            continue
    
        if t == "location":
            if is_multi:
                raise ValueError("Did not expect multi-select location attribute")
            
            # Assert there is one JSON schema property per column on the value  
            # The name of each property should be the attribute's api_slug + field e.g. "my_location_line_1"
            assert properties[f"{slug}_line_1"] == {"type": ["string", "null"]}
            assert properties[f"{slug}_line_2"] == {"type": ["string", "null"]}
            assert properties[f"{slug}_line_3"] == {"type": ["string", "null"]}
            assert properties[f"{slug}_line_4"] == {"type": ["string", "null"]}
            assert properties[f"{slug}_locality"] == {"type": ["string", "null"]}
            assert properties[f"{slug}_region"] == {"type": ["string", "null"]}
            assert properties[f"{slug}_postcode"] == {"type": ["string", "null"]}
            assert properties[f"{slug}_country_code"] == {"type": ["string", "null"]}
            assert properties[f"{slug}_longitude"] == {"type": ["string", "null"]}
            assert properties[f"{slug}_latitude"] == {"type": ["string", "null"]}
            continue
        
        schema = properties[attribute["api_slug"]]

        match (t, is_multi):
            case ("text", _):
                assert schema == {"type": ["string", "null"]}
            case ("number", _):
                assert schema == {"type": ["number", "null"]}
            case ("checkbox", _):
                assert schema == {"type": "boolean"}
            case ("currency", _):
                assert schema == {"type": ["number", "null"]}
            case ("date", _):
                assert schema == {"type": ["string", "null"], "format": "date"}
            case ("timestamp", _):
                assert schema == {"type": ["string", "null"], "format": "date-time", "airbyte_type": "timestamp_with_timezone"}
            case ("rating", _):
                assert schema == {"type": ["integer", "null"]}
            case ("status", _):
                assert schema == {"type": ["string", "null"]}  # ID
            case ("select", True):
                assert schema == {"type": "array", "items": {"type": "string"}}
            case ("select", False):
                assert schema == {"type": ["string", "null"]}
            case ("record-reference", True):
                assert schema == {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "target_object": {"type": "string"},
                            "target_record_id": {"type": "string"},
                        },
                    },
                }
            case ("record-reference", False):
                assert schema == {
                    "type": ["object", "null"],
                    "properties": {
                        "target_object": {"type": "string"},
                        "target_record_id": {"type": "string"},
                    },
                }
            case ("actor-reference", True):
                assert schema == {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "referenced_actor_id": {"type": "string"},
                            "referenced_actor_type": {"type": "string"},
                        },
                    },
                }
            case ("actor-reference", False):
                assert schema == {
                    "type": ["object", "null"],
                    "properties": {
                        "referenced_actor_id": {"type": "string"},
                        "referenced_actor_type": {"type": "string"},
                    },
                }
            case ("domain", True):
                assert schema == {"type": "array", "items": {"type": "string"}}
            case ("domain", False):
                raise ValueError("Did not expect domain attribute to be single-select")
            case ("email-address", True):
                assert schema == {"type": "array", "items": {"type": "string"}}
            case ("email-address", False):
                assert schema == {"type": ["string", "null"]}
            case ("phone-number", True):
                assert schema == {"type": "array", "items": {"type": "string"}}
            case ("phone-number", False):
                raise ValueError("Did not expect phone number attribute to be single-select")
