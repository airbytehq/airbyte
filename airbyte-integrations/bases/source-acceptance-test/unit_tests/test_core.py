#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    ConnectorSpecification,
    Type,
)
from source_acceptance_test.config import BasicReadTestConfig
from source_acceptance_test.tests.test_core import TestBasicRead as _TestBasicRead
from source_acceptance_test.tests.test_core import TestDiscovery as _TestDiscovery
from source_acceptance_test.tests.test_core import TestSpec as _TestSpec


@pytest.mark.parametrize(
    "schema, cursors, should_fail",
    [
        ({}, ["created"], True),
        ({"properties": {"created": {"type": "string"}}}, ["created"], False),
        ({"properties": {"created_at": {"type": "string"}}}, ["created"], True),
        ({"properties": {"created": {"type": "string"}}}, ["updated", "created"], True),
        ({"properties": {"updated": {"type": "object", "properties": {"created": {"type": "string"}}}}}, ["updated", "created"], False),
        ({"properties": {"created": {"type": "object", "properties": {"updated": {"type": "string"}}}}}, ["updated", "created"], True),
    ],
)
def test_discovery(schema, cursors, should_fail):
    t = _TestDiscovery()
    discovered_catalog = {
        "test_stream": AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema, "default_cursor_field": cursors})
    }
    if should_fail:
        with pytest.raises(AssertionError):
            t.test_defined_cursors_exist_in_schema(None, discovered_catalog)
    else:
        t.test_defined_cursors_exist_in_schema(None, discovered_catalog)


@pytest.mark.parametrize(
    "schema, record, should_fail",
    [
        ({"type": "object"}, {"aa": 23}, False),
        ({"type": "object"}, {}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"aa": 23}, True),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"created": "23"}, False),
        ({"type": "object", "properties": {"created": {"type": "string"}}}, {"root": {"created": "23"}}, True),
        # Recharge shop stream case
        (
            {"type": "object", "properties": {"shop": {"type": ["null", "object"]}, "store": {"type": ["null", "object"]}}},
            {"shop": {"a": "23"}, "store": {"b": "23"}},
            False,
        ),
    ],
)
def test_read(schema, record, should_fail):
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj({"name": "test_stream", "json_schema": schema}),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            )
        ]
    )
    input_config = BasicReadTestConfig()
    docker_runner_mock = MagicMock()
    docker_runner_mock.call_read.return_value = [
        AirbyteMessage(type=Type.RECORD, record=AirbyteRecordMessage(stream="test_stream", data=record, emitted_at=111))
    ]
    t = _TestBasicRead()
    if should_fail:
        with pytest.raises(AssertionError, match="stream should have some fields mentioned by json schema"):
            t.test_read(None, catalog, input_config, [], docker_runner_mock, MagicMock())
    else:
        t.test_read(None, catalog, input_config, [], docker_runner_mock, MagicMock())


@pytest.mark.parametrize(
    "connector_spec, expected_error",
    [
        # SUCCESS: no authSpecification specified
        (ConnectorSpecification(connectionSpecification={}), ""),
        # FAIL: Field specified in root object does not exist
        (
            ConnectorSpecification(
                connectionSpecification={"type": "object"},
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 0],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "Specified oauth fields are missed from spec schema:",
        ),
        # SUCCESS: Empty root object
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "client_id": {"type": "string"},
                        "client_secret": {"type": "string"},
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": [],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "",
        ),
        # FAIL: Some oauth fields missed
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "properties": {
                                "client_id": {"type": "string"},
                                "client_secret": {"type": "string"},
                                "access_token": {"type": "string"},
                            },
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 0],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "Specified oauth fields are missed from spec schema:",
        ),
        # SUCCESS: case w/o oneOf property
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "properties": {
                                "client_id": {"type": "string"},
                                "client_secret": {"type": "string"},
                                "access_token": {"type": "string"},
                                "refresh_token": {"type": "string"},
                            },
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials"],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "",
        ),
        # SUCCESS: case w/ oneOf property
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "properties": {
                                        "client_id": {"type": "string"},
                                        "client_secret": {"type": "string"},
                                        "access_token": {"type": "string"},
                                        "refresh_token": {"type": "string"},
                                    }
                                },
                                {
                                    "properties": {
                                        "api_key": {"type": "string"},
                                    }
                                },
                            ],
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 0],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "",
        ),
        # FAIL: Wrong root object index
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "properties": {
                                        "client_id": {"type": "string"},
                                        "client_secret": {"type": "string"},
                                        "access_token": {"type": "string"},
                                        "refresh_token": {"type": "string"},
                                    }
                                },
                                {
                                    "properties": {
                                        "api_key": {"type": "string"},
                                    }
                                },
                            ],
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 1],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "Specified oauth fields are missed from spec schema:",
        ),
        # SUCCESS: root object index equal to 1
        (
            ConnectorSpecification(
                connectionSpecification={
                    "type": "object",
                    "properties": {
                        "credentials": {
                            "type": "object",
                            "oneOf": [
                                {
                                    "properties": {
                                        "api_key": {"type": "string"},
                                    }
                                },
                                {
                                    "properties": {
                                        "client_id": {"type": "string"},
                                        "client_secret": {"type": "string"},
                                        "access_token": {"type": "string"},
                                        "refresh_token": {"type": "string"},
                                    }
                                },
                            ],
                        }
                    },
                },
                authSpecification={
                    "auth_type": "oauth2.0",
                    "oauth2Specification": {
                        "rootObject": ["credentials", 1],
                        "oauthFlowInitParameters": [["client_id"], ["client_secret"]],
                        "oauthFlowOutputParameters": [["access_token"], ["refresh_token"]],
                    },
                },
            ),
            "",
        ),
    ],
)
def test_validate_oauth_flow(connector_spec, expected_error):
    t = _TestSpec()
    if expected_error:
        with pytest.raises(AssertionError, match=expected_error):
            t.test_oauth_flow_parameters(connector_spec)
    else:
        t.test_oauth_flow_parameters(connector_spec)


@pytest.fixture
def records():
    test1_records = [
        {
            "id": 123,
            "application_id": 123,
            "external_event_id": "123456789",
            "start": {"date_time": "2021-12-12T13:15:00.000Z"},
            "end": {"date_time": "2021-12-12T14:15:00.000Z"},
            "location": None,
            "video_conferencing_url": None,
            "status": "scheduled",
            "created_at": "2021-10-10T16:21:44.107Z",
            "updated_at": "2021-10-10T16:21:44.252Z",
            "interview": {"id": 123, "name": "Preliminary Screening Call"},
            "organizer": {"id": 123, "first_name": "Test", "last_name": "Admin", "name": "Test Admin", "employee_id": None},
            "interviewers": [
                {
                    "id": 123,
                    "employee_id": None,
                    "name": "Admin",
                    "email": "test@example.com",
                    "response_status": "accepted",
                    "scorecard_id": None,
                }
            ],
        },
        {
            "id": 123,
            "application_id": 123,
            "external_event_id": "12345678",
            "start": {"date_time": "2021-12-13T13:15:00.000Z"},
            "end": {"date_time": "2021-12-13T14:15:00.000Z"},
            "location": None,
            "video_conferencing_url": None,
            "status": "scheduled",
            "created_at": "2021-10-10T16:22:04.561Z",
            "updated_at": "2021-10-10T16:22:04.561Z",
            "interview": {"id": 123, "name": "Preliminary Screening Call"},
            "organizer": {"id": 123, "first_name": "Test", "last_name": "Admin", "name": "Test Admin", "employee_id": None},
            "interviewers": [
                {
                    "id": 123,
                    "employee_id": None,
                    "name": "Test Admin",
                    "email": "test@example.com",
                    "response_status": "accepted",
                    "scorecard_id": None,
                }
            ],
        },
        {
            "id": 123,
            "application_id": 123,
            "external_event_id": "1234567",
            "start": {"date_time": "2021-12-14T13:15:00.000Z"},
            "end": {"date_time": "2021-12-14T14:15:00.000Z"},
            "location": None,
            "video_conferencing_url": None,
            "status": "scheduled",
            "created_at": "2021-10-10T16:22:13.681Z",
            "updated_at": "2021-10-10T16:22:13.681Z",
            "interview": {"id": 123, "name": "Preliminary Screening Call"},
            "organizer": {"id": 123, "first_name": "Test", "last_name": "Admin", "name": "Test Admin", "employee_id": None},
            "interviewers": [
                {
                    "id": 123,
                    "employee_id": None,
                    "name": "Test Admin",
                    "email": "test@example.com",
                    "response_status": "accepted",
                    "scorecard_id": None,
                }
            ],
        },
    ]
    test2_records = [
        {
            "website_addresses": [],
            "updated_at": "2020-11-24T23:24:37.050Z",
            "title": None,
            "tags": [],
            "social_media_addresses": [],
            "recruiter": None,
            "photo_url": None,
            "phone_numbers": [],
            "last_name": "Test",
            "last_activity": "2020-11-24T23:24:37.049Z",
            "is_private": False,
            "id": 123,
            "first_name": "Test",
            "employments": [],
            "email_addresses": [],
            "educations": [],
            "created_at": "2020-11-24T23:24:37.018Z",
            "coordinator": None,
            "company": None,
            "can_email": True,
            "attachments": [],
            "applications": [
                {
                    "status": "active",
                    "source": {"public_name": "TEST", "id": 123},
                    "rejection_reason": None,
                    "rejection_details": None,
                    "rejected_at": None,
                    "prospective_office": None,
                    "prospective_department": None,
                    "prospect_detail": {
                        "prospect_stage": None,
                        "prospect_pool": None,
                        "prospect_owner": {"name": "Test Name", "id": 123},
                    },
                    "prospect": True,
                    "location": None,
                    "last_activity_at": "2020-11-24T23:24:37.049Z",
                    "jobs": [],
                    "job_post_id": None,
                    "id": 123,
                    "current_stage": None,
                    "credited_to": {"name": "Test Name", "last_name": "Test", "id": 123, "first_name": "Name", "employee_id": None},
                    "candidate_id": 123,
                    "attachments": [],
                    "applied_at": "2020-11-24T23:24:37.023Z",
                    "answers": [],
                }
            ],
            "application_ids": [123],
            "addresses": [],
        },
        {
            "website_addresses": [],
            "updated_at": "2020-11-24T23:25:13.806Z",
            "title": None,
            "tags": [],
            "social_media_addresses": [],
            "recruiter": None,
            "photo_url": None,
            "phone_numbers": [],
            "last_name": "Test2",
            "last_activity": "2020-11-24T23:25:13.804Z",
            "is_private": False,
            "id": 123,
            "first_name": "Test2",
            "employments": [],
            "email_addresses": [],
            "educations": [],
            "created_at": "2020-11-24T23:25:13.777Z",
            "coordinator": None,
            "company": None,
            "can_email": True,
            "attachments": [],
            "applications": [
                {
                    "status": "active",
                    "source": {"public_name": "Jobs page on your website", "id": 123},
                    "rejection_reason": None,
                    "rejection_details": None,
                    "rejected_at": None,
                    "prospective_office": None,
                    "prospective_department": None,
                    "prospect_detail": {
                        "prospect_stage": None,
                        "prospect_pool": None,
                        "prospect_owner": {"name": "Test Name", "id": 123},
                    },
                    "prospect": True,
                    "location": None,
                    "last_activity_at": "2020-11-24T23:25:13.804Z",
                    "jobs": [],
                    "job_post_id": None,
                    "id": 123,
                    "current_stage": None,
                    "credited_to": {"name": "Test Name", "last_name": "Test", "id": 123, "first_name": "Name", "employee_id": None},
                    "candidate_id": 123,
                    "attachments": [],
                    "applied_at": "2020-11-24T23:25:13.781Z",
                    "answers": [],
                }
            ],
            "application_ids": [123],
            "addresses": [],
        },
        {
            "website_addresses": [],
            "updated_at": "2020-11-24T23:28:19.781Z",
            "title": None,
            "tags": [],
            "social_media_addresses": [],
            "recruiter": None,
            "photo_url": None,
            "phone_numbers": [],
            "last_name": "Lastname",
            "last_activity": "2020-11-24T23:28:19.779Z",
            "is_private": False,
            "id": 123,
            "first_name": "Name",
            "employments": [],
            "email_addresses": [],
            "educations": [],
            "created_at": "2020-11-24T23:28:19.710Z",
            "coordinator": None,
            "company": None,
            "can_email": True,
            "attachments": [],
            "applications": [
                {
                    "status": "active",
                    "source": {"public_name": "Internal Applicant", "id": 123},
                    "rejection_reason": None,
                    "rejection_details": None,
                    "rejected_at": None,
                    "prospective_office": None,
                    "prospective_department": None,
                    "prospect_detail": {"prospect_stage": None, "prospect_pool": None, "prospect_owner": None},
                    "prospect": False,
                    "location": None,
                    "last_activity_at": "2020-11-24T23:28:19.779Z",
                    "jobs": [{"name": "Test job", "id": 123}],
                    "job_post_id": None,
                    "id": 123,
                    "current_stage": {"name": "Preliminary Phone Screen", "id": 123},
                    "credited_to": {"name": "Test Name", "last_name": "Test", "id": 123, "first_name": "Name", "employee_id": None},
                    "candidate_id": 123,
                    "attachments": [],
                    "applied_at": "2020-11-24T23:28:19.712Z",
                    "answers": [],
                }
            ],
            "application_ids": [123],
            "addresses": [],
        },
        {
            "website_addresses": [],
            "updated_at": "2020-12-05T02:50:25.823Z",
            "title": None,
            "tags": [],
            "social_media_addresses": [],
            "recruiter": None,
            "photo_url": None,
            "phone_numbers": [],
            "last_name": "D",
            "last_activity": "2020-12-05T02:50:25.811Z",
            "is_private": False,
            "id": 123,
            "first_name": "Test",
            "employments": [],
            "email_addresses": [],
            "educations": [],
            "created_at": "2020-11-24T23:30:14.386Z",
            "coordinator": None,
            "company": None,
            "can_email": True,
            "attachments": [{"url": "https://test.com", "type": "offer_packet", "filename": "test.pdf"}],
            "applications": [
                {
                    "status": "active",
                    "source": {"public_name": "Referral", "id": 123},
                    "rejection_reason": None,
                    "rejection_details": None,
                    "rejected_at": None,
                    "prospective_office": None,
                    "prospective_department": None,
                    "prospect_detail": {"prospect_stage": None, "prospect_pool": None, "prospect_owner": None},
                    "prospect": False,
                    "location": None,
                    "last_activity_at": "2020-12-05T02:50:25.811Z",
                    "jobs": [{"name": "Test Job 2", "id": 123}],
                    "job_post_id": None,
                    "id": 123,
                    "current_stage": {"name": "Offer", "id": 123},
                    "credited_to": {"name": "Test Name", "last_name": "Test", "id": 123, "first_name": "Name", "employee_id": None},
                    "candidate_id": 123,
                    "attachments": [
                        {
                            "url": "https://test.com",
                            "type": "offer_packet",
                            "filename": "test",
                        }
                    ],
                    "applied_at": "2020-11-24T23:30:14.394Z",
                    "answers": [],
                }
            ],
            "application_ids": [123],
            "addresses": [],
        },
        {
            "website_addresses": [],
            "updated_at": "2021-09-29T16:38:03.672Z",
            "title": None,
            "tags": [],
            "social_media_addresses": [],
            "recruiter": None,
            "photo_url": None,
            "phone_numbers": [],
            "last_name": "User",
            "last_activity": "2021-09-29T16:38:03.660Z",
            "is_private": False,
            "id": 123,
            "first_name": "Test",
            "employments": [],
            "email_addresses": [],
            "educations": [],
            "created_at": "2021-09-29T16:37:27.585Z",
            "coordinator": None,
            "company": None,
            "can_email": True,
            "attachments": [],
            "applications": [
                {
                    "status": "rejected",
                    "source": {"public_name": "Test agency", "id": 123},
                    "rejection_reason": {"type": {"name": "We rejected them", "id": 123}, "name": "Test", "id": 123},
                    "rejection_details": {},
                    "rejected_at": "2021-09-29T16:38:03.637Z",
                    "prospective_office": None,
                    "prospective_department": None,
                    "prospect_detail": {"prospect_stage": None, "prospect_pool": None, "prospect_owner": None},
                    "prospect": False,
                    "location": None,
                    "last_activity_at": "2021-09-29T16:38:03.660Z",
                    "jobs": [{"name": "Test job", "id": 123}],
                    "job_post_id": None,
                    "id": 123,
                    "current_stage": {"name": "Phone Interview", "id": 5245805003},
                    "credited_to": {"name": "Test Name", "last_name": "Test", "id": 123, "first_name": "Name", "employee_id": None},
                    "candidate_id": 123,
                    "attachments": [],
                    "applied_at": "2021-09-29T16:37:27.589Z",
                    "answers": [],
                }
            ],
            "application_ids": [123],
            "addresses": [],
        },
        {
            "website_addresses": [],
            "updated_at": "2021-10-10T16:22:13.718Z",
            "title": None,
            "tags": [],
            "social_media_addresses": [],
            "recruiter": None,
            "photo_url": None,
            "phone_numbers": [],
            "last_name": "Scheduled Interview",
            "last_activity": "2021-10-10T16:22:13.708Z",
            "is_private": False,
            "id": 123,
            "first_name": "Test",
            "employments": [],
            "email_addresses": [{"value": "test@example.com", "type": "personal"}],
            "educations": [],
            "created_at": "2021-09-29T17:20:36.038Z",
            "coordinator": None,
            "company": None,
            "can_email": True,
            "attachments": [],
            "applications": [
                {
                    "status": "active",
                    "source": {"public_name": "Test agency", "id": 123},
                    "rejection_reason": None,
                    "rejection_details": None,
                    "rejected_at": None,
                    "prospective_office": None,
                    "prospective_department": None,
                    "prospect_detail": {"prospect_stage": None, "prospect_pool": None, "prospect_owner": None},
                    "prospect": False,
                    "location": None,
                    "last_activity_at": "2021-10-10T16:22:13.708Z",
                    "jobs": [{"name": "Test job", "id": 123}],
                    "job_post_id": None,
                    "id": 123,
                    "current_stage": {"name": "Preliminary Phone Screen", "id": 123},
                    "credited_to": {
                        "name": "Test Admin",
                        "last_name": "Admin",
                        "id": 4218085003,
                        "first_name": "Test",
                        "employee_id": None,
                    },
                    "candidate_id": 123,
                    "attachments": [],
                    "applied_at": "2021-09-29T17:20:36.063Z",
                    "answers": [],
                }
            ],
            "application_ids": [123],
            "addresses": [],
        },
        {
            "website_addresses": [],
            "updated_at": "2021-11-03T19:56:07.423Z",
            "title": None,
            "tags": [],
            "social_media_addresses": [],
            "recruiter": None,
            "photo_url": None,
            "phone_numbers": [],
            "last_name": "Candidate",
            "last_activity": "2021-11-03T19:56:07.402Z",
            "is_private": False,
            "id": 123,
            "first_name": "Test",
            "employments": [],
            "email_addresses": [{"value": "test@example.com", "type": "work"}],
            "educations": [],
            "created_at": "2021-11-03T19:51:14.639Z",
            "coordinator": None,
            "company": None,
            "can_email": True,
            "attachments": [],
            "applications": [
                {
                    "status": "active",
                    "source": {"public_name": "Test agency", "id": 123},
                    "rejection_reason": None,
                    "rejection_details": None,
                    "rejected_at": None,
                    "prospective_office": None,
                    "prospective_department": None,
                    "prospect_detail": {"prospect_stage": None, "prospect_pool": None, "prospect_owner": None},
                    "prospect": False,
                    "location": None,
                    "last_activity_at": "2021-11-03T19:56:07.402Z",
                    "jobs": [{"name": "Test job 3", "id": 123}],
                    "job_post_id": 123,
                    "id": 123,
                    "current_stage": {"name": "Application Review", "id": 123},
                    "credited_to": {"name": "Test Name", "last_name": "Test", "id": 123, "first_name": "Name", "employee_id": None},
                    "candidate_id": 123,
                    "attachments": [],
                    "applied_at": "2021-11-03T19:51:14.644Z",
                    "answers": [{"question": "Website", "answer": None}, {"question": "LinkedIn Profile", "answer": None}],
                }
            ],
            "application_ids": [123],
            "addresses": [],
        },
        {
            "website_addresses": [],
            "updated_at": "2021-11-22T08:41:55.716Z",
            "title": None,
            "tags": [],
            "social_media_addresses": [],
            "recruiter": None,
            "photo_url": None,
            "phone_numbers": [],
            "last_name": "Name",
            "last_activity": "2021-11-22T08:41:55.713Z",
            "is_private": False,
            "id": 123,
            "first_name": "Yurii",
            "employments": [],
            "email_addresses": [],
            "educations": [],
            "created_at": "2021-11-22T08:41:55.634Z",
            "coordinator": None,
            "company": None,
            "can_email": True,
            "attachments": [],
            "applications": [
                {
                    "status": "active",
                    "source": {"public_name": "Bubblesort", "id": 123},
                    "rejection_reason": None,
                    "rejection_details": None,
                    "rejected_at": None,
                    "prospective_office": None,
                    "prospective_department": None,
                    "prospect_detail": {"prospect_stage": None, "prospect_pool": None, "prospect_owner": None},
                    "prospect": False,
                    "location": None,
                    "last_activity_at": "2021-11-22T08:41:55.713Z",
                    "jobs": [{"name": "Copy of Test Job 2", "id": 123}],
                    "job_post_id": None,
                    "id": 123,
                    "current_stage": {"name": "Application Review", "id": 123},
                    "credited_to": {
                        "name": "emily.brooks+airbyte_integration@Test.io",
                        "last_name": None,
                        "id": 123,
                        "first_name": None,
                        "employee_id": None,
                    },
                    "candidate_id": 123,
                    "attachments": [],
                    "applied_at": "2021-11-22T08:41:55.640Z",
                    "answers": [],
                }
            ],
            "application_ids": [123],
            "addresses": [],
        },
    ]
    recs = [AirbyteRecordMessage(stream="test1", data=r, emitted_at=111) for r in test1_records]
    recs.extend([AirbyteRecordMessage(stream="test2", data=r, emitted_at=111) for r in test2_records])
    return recs


@pytest.fixture
def configured_catalog():
    catalog = ConfiguredAirbyteCatalog(
        streams=[
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj(
                    {
                        "name": "test1",
                        "json_schema": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "application_id": {"type": ["null", "integer"]},
                                "external_event_id": {"type": ["null", "string"]},
                                "start": {"type": ["null", "string"]},
                                "end": {
                                    "type": ["null", "object"],
                                    "properties": {"date_time": {"type": ["null", "string"], "format": "date-time"}},
                                },
                                "location": {"type": ["null", "string"]},
                                "video_conferencing_url": {"type": ["null", "string"]},
                                "status": {"type": ["null", "string"]},
                                "created_at": {"type": ["null", "string"], "format": "date-time"},
                                "updated_at": {"type": ["null", "string"], "format": "date-time"},
                                "interview": {
                                    "type": ["null", "object"],
                                    "properties": {"id": {"type": ["null", "integer"]}, "name": {"type": ["null", "string"]}},
                                },
                                "organizer": {
                                    "type": ["null", "object"],
                                    "properties": {
                                        "id": {"type": ["null", "integer"]},
                                        "first_name": {"type": ["null", "string"]},
                                        "last_name": {"type": ["null", "string"]},
                                        "name": {"type": ["null", "string"]},
                                        "employee_id": {"type": ["null", "string"]},
                                    },
                                },
                                "interviewers": {
                                    "type": ["null", "array"],
                                    "items": {
                                        "type": ["null", "object"],
                                        "properties": {
                                            "id": {"type": ["null", "integer"]},
                                            "employee_id": {"type": ["null", "string"]},
                                            "name": {"type": ["null", "string"]},
                                            "email": {"type": ["null", "string"]},
                                            "response_status": {"type": ["null", "string"]},
                                            "scorecard_id": {"type": ["null", "integer"]},
                                        },
                                    },
                                },
                            },
                        },
                    }
                ),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            ),
            ConfiguredAirbyteStream(
                stream=AirbyteStream.parse_obj(
                    {
                        "name": "test2",
                        "json_schema": {
                            "type": "object",
                            "properties": {
                                "website_addresses": {"type": "array"},
                                "updated_at": {"type": "string"},
                                "title": {"type": ["null", "string"]},
                                "tags": {"type": "array"},
                                "social_media_addresses": {"type": "array"},
                                "recruiter": {"type": ["null", "string"]},
                                "photo_url": {"type": ["null", "string"]},
                                "phone_numbers": {"type": "array"},
                                "last_name": {"type": "string"},
                                "last_activity": {"type": "string"},
                                "is_private": {"type": "boolean"},
                                "id": {"type": "integer"},
                                "first_name": {"type": "string"},
                                "employments": {"type": "array"},
                                "email_addresses": {"type": "array"},
                                "educations": {"type": "array"},
                                "created_at": {"type": "string"},
                                "coordinator": {"type": ["null", "string"]},
                                "company": {"type": ["null", "string"]},
                                "can_email": {"type": "boolean"},
                                "attachments": {"type": "array"},
                                "applications": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "source": {
                                                "type": "object",
                                                "properties": {"public_name": {"type": "string"}, "id": {"type": "integer"}},
                                            },
                                            "rejection_reason": {
                                                "type": ["null", "object"],
                                                "properties": {
                                                    "id": {"type": ["null", "integer"]},
                                                    "name": {"type": ["null", "string"]},
                                                    "type": {
                                                        "type": ["null", "object"],
                                                        "properties": {
                                                            "id": {"type": ["null", "integer"]},
                                                            "name": {"type": ["null", "string"]},
                                                        },
                                                    },
                                                },
                                            },
                                            "rejection_details": {
                                                "type": ["null", "object"],
                                                "properties": {
                                                    "custom_fields": {"type": ["null", "object"]},
                                                    "keyed_custom_fields": {"type": ["null", "object"]},
                                                },
                                            },
                                            "rejected_at": {"type": ["null", "string"]},
                                            "prospective_office": {"type": ["null", "string"]},
                                            "prospective_department": {"type": ["null", "string"]},
                                            "prospect_detail": {
                                                "type": "object",
                                                "properties": {
                                                    "prospect_stage": {"type": ["null", "string"]},
                                                    "prospect_pool": {"type": ["null", "string"]},
                                                    "prospect_owner": {
                                                        "type": ["null", "object"],
                                                        "properties": {"name": {"type": "string"}, "id": {"type": "integer"}},
                                                    },
                                                },
                                            },
                                            "prospect": {"type": "boolean"},
                                            "location": {"type": ["null", "string"]},
                                            "last_activity_at": {"type": "string"},
                                            "jobs": {"type": "array"},
                                            "id": {"type": "integer"},
                                            "current_stage": {
                                                "type": ["null", "object"],
                                                "properties": {"name": {"type": "string"}, "id": {"type": "integer"}},
                                            },
                                            "credited_to": {
                                                "type": "object",
                                                "properties": {
                                                    "name": {"type": "string"},
                                                    "last_name": {"type": "string"},
                                                    "id": {"type": "integer"},
                                                    "first_name": {"type": "string"},
                                                    "employee_id": {"type": ["null", "integer"]},
                                                },
                                            },
                                            "candidate_id": {"type": "integer"},
                                            "attachments": {"type": "array"},
                                            "applied_at": {"type": "string"},
                                            "answers": {"type": "array"},
                                        },
                                    },
                                },
                                "application_ids": {"type": "array", "items": {"type": "integer"}},
                                "addresses": {"type": "array"},
                            },
                        },
                    }
                ),
                sync_mode="full_refresh",
                destination_sync_mode="overwrite",
            ),
        ]
    )
    return catalog


def test_validate_empty_streams(records, configured_catalog):
    t = _TestBasicRead()
    with pytest.raises(AssertionError) as excinfo:
        t._validate_field_appears_at_least_once(records=records, configured_catalog=configured_catalog)

    expected_excinfo = "Following streams has records with fields, that are either null or not present in each output record:\n  `test1` stream has `[('location',), ('video_conferencing_url',), ('organizer', 'employee_id'), ('interviewers', 'employee_id'), ('interviewers', 'scorecard_id')]` empty fields\n  `test2` stream has `[('website_addresses',), ('title',), ('tags',), ('social_media_addresses',), ('recruiter',), ('photo_url',), ('phone_numbers',), ('is_private',), ('employments',), ('educations',), ('coordinator',), ('company',), ('applications', 'source', 'rejection_reason'), ('applications', 'source', 'rejection_details'), ('applications', 'source', 'rejected_at'), ('applications', 'source', 'prospective_office'), ('applications', 'source', 'prospective_department'), ('applications', 'source', 'prospect_detail', 'prospect_stage'), ('applications', 'source', 'prospect_detail', 'prospect_pool'), ('applications', 'source', 'prospect_detail', 'prospect_owner', 'location'), ('applications', 'source', 'prospect_detail', 'prospect_owner', 'jobs'), ('applications', 'source', 'prospect_detail', 'prospect_owner', 'current_stage'), ('applications', 'source', 'prospect_detail', 'prospect_owner', 'credited_to', 'employee_id'), ('applications', 'source', 'prospect_detail', 'prospect_owner', 'credited_to', 'attachments'), ('applications', 'source', 'prospect_detail', 'prospect_owner', 'credited_to', 'answers'), ('addresses',), ('applications', 'source', 'prospect_detail', 'prospect_owner'), ('applications', 'source', 'prospect_detail', 'prospect'), ('applications', 'source', 'prospect_detail', 'location'), ('applications', 'source', 'prospect_detail', 'jobs', 'current_stage', 'credited_to', 'employee_id'), ('applications', 'source', 'prospect_detail', 'jobs', 'current_stage', 'credited_to', 'attachments'), ('applications', 'source', 'prospect_detail', 'jobs', 'current_stage', 'credited_to', 'answers'), ('applications', 'source', 'prospect_detail', 'jobs', 'current_stage', 'credited_to', 'attachments', 'answers'), ('applications', 'source', 'rejection_reason', 'type', 'rejection_details'), ('applications', 'source', 'rejection_reason', 'type', 'prospective_office'), ('applications', 'source', 'rejection_reason', 'type', 'prospective_department'), ('applications', 'source', 'rejection_reason', 'type', 'prospect_detail', 'prospect_stage'), ('applications', 'source', 'rejection_reason', 'type', 'prospect_detail', 'prospect_pool'), ('applications', 'source', 'rejection_reason', 'type', 'prospect_detail', 'prospect_owner'), ('applications', 'source', 'rejection_reason', 'type', 'prospect_detail', 'prospect'), ('applications', 'source', 'rejection_reason', 'type', 'prospect_detail', 'location'), ('applications', 'source', 'rejection_reason', 'type', 'prospect_detail', 'jobs', 'current_stage', 'credited_to', 'employee_id'), ('applications', 'source', 'rejection_reason', 'type', 'prospect_detail', 'jobs', 'current_stage', 'credited_to', 'attachments'), ('applications', 'source', 'rejection_reason', 'type', 'prospect_detail', 'jobs', 'current_stage', 'credited_to', 'answers')]` empty fields"
    assert expected_excinfo in str(excinfo.value)
