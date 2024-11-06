# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from unit_tests.integration.rest.test_base import TestBase


class TestPerson(TestBase):
    space = "person"

class TestPeople(TestPerson):
    stream_name = "people"
    path = "people"
