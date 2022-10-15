#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from sqlite3 import DatabaseError

from firebase_admin import db
import pytest

from source_firebase_realtime_database.firebase_rtdb import Client


pytest_plugins = ("source_acceptance_test.plugin",)


def generate_test_records(path):
    records = {}
    with open(path) as f:
        for line in f.readlines():
            rec = json.loads(line)
            data = rec["data"]
            records[data["key"]] = json.loads(data["value"])

    return records


@pytest.fixture(scope="session", autouse=True)
def connector_setup():
    records = generate_test_records("integration_tests/expected_records.txt")

    with open("secrets/admin_config.json", "r") as f:
        conf = json.load(f)
    path = conf["path"]
    database_name = conf["database_name"]
    google_application_credentials = conf["google_application_credentials"]
    client = Client(path)
    client.initialize(database_name, google_application_credentials)
    client.set_records(records)

    yield

    client.delete_records()
