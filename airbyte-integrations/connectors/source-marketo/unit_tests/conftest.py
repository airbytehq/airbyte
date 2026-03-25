#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import os.path
import sys
import time
from typing import Any, Mapping

from datetime import datetime, timedelta

import pytest
from source_marketo.source import SourceMarketo

from airbyte_cdk.sources.declarative.declarative_stream import DeclarativeStream


START_DATE = datetime.utcnow() - timedelta(days=75)


@pytest.fixture(autouse=True)
def mock_requests(requests_mock):
    requests_mock.register_uri(
        "GET", "https://602-euo-598.mktorest.com/identity/oauth/token", json={"access_token": "token", "expires_in": 3600}
    )
    # Dynamic streams resolution requires fetching activity types
    requests_mock.register_uri(
        "GET",
        "https://602-euo-598.mktorest.com/rest/v1/activities/types.json",
        json={
            "success": True,
            "result": [
                {
                    "id": 6,
                    "name": "send_email",
                    "description": "Send Marketo Email",
                    "primaryAttribute": {"name": "Mailing ID", "dataType": "integer"},
                    "attributes": [
                        {"name": "Campaign Run ID", "dataType": "integer"},
                        {"name": "Choice Number", "dataType": "integer"},
                    ],
                }
            ],
        },
    )


@pytest.fixture
def config():
    return {
        "client_id": "client-id",
        "client_secret": "********",
        "domain_url": "https://602-EUO-598.mktorest.com",
        "start_date": START_DATE.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_in_days": 30,
    }


@pytest.fixture
def activity():
    return {
        "id": 6,
        "name": "send_email",
        "description": "Send Marketo Email to a person",
        "primaryAttribute": {"name": "Mailing ID", "dataType": "integer"},
        "attributes": [
            {"name": "Campaign Run ID", "dataType": "integer"},
            {"name": "Choice Number", "dataType": "integer"},
            {"name": "Has Predictive", "dataType": "boolean"},
            {"name": "Step ID", "dataType": "integer"},
            {"name": "Test Variant", "dataType": "integer"},
        ],
    }


@pytest.fixture
def file_generator(faker):
    def _generator(min_size: int):
        print(f"Generating a test file of {min_size // 1024 ** 2} MB, this could take some time")

        def fake_records_gen():
            new_line = "\n"
            for i in range(1000):
                yield (
                    f"{str(faker.random_int())},{faker.random_int()},{faker.date_of_birth()},{faker.random_int()},"
                    f"{faker.random_int()},{faker.email()},{faker.postcode()}{new_line}"
                )

        size, records = 0, 0
        path = os.path.realpath(str(time.time()))
        with open(path, "w") as output:
            output.write("marketoGUID,leadId,activityDate,activityTypeId,campaignId,primaryAttributeValueId,primaryAttributeValue\n")
            while size < min_size:
                frg = fake_records_gen()
                print("Writing another 1000 records..")
                for person in frg:
                    output.write(person)
                    records += 1
                    size += sys.getsizeof(person)
        print(f"Finished: {records} records written to {path}")
        return path, records

    return _generator


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> DeclarativeStream:
    source = SourceMarketo()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]


@pytest.fixture(autouse=True)
def mock_auth(requests_mock) -> None:
    requests_mock.post("/identity/oauth/token", json={"access_token": "access_token", "expires_in": 3600})
