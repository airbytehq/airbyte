#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import pytest
from airbyte_cdk.models import ConfiguredAirbyteCatalog, ConfiguredAirbyteStream, AirbyteStream
from source_acceptance_test.utils.asserts import verify_records_schema


@pytest.fixture(name="record_schema")
def schema_fixture():
    return {
        "properties": {
            "text_or_null": {
                "type": ["null", "string"]
            },
            "number_or_null": {
                "type": ["null", "number"]
            },
            "text": {
                "type": ["null", "string"]
            },
            "number": {
                "type": ["null", "number"]
            },
        },
        "type": ["null", "object"]
    }


@pytest.fixture(name="configured_catalog")
def catalog_fixture() -> ConfiguredAirbyteCatalog:
    return ConfiguredAirbyteCatalog(streams=[
        ConfiguredAirbyteStream(stream=AirbyteStream)
    ])


def test_verify_records_schema(configured_catalog: ConfiguredAirbyteCatalog):
    records = [
        {
            "text_or_null": 123,  # wrong format
            "number_or_null": 10.3,
            "text": "text",
            "number": "text",  # wrong format
        },
        {
            "text_or_null": 123,
            "number_or_null": None,
            "text": None,  # wrong value
            "number": None,  # wrong value
        },
        {
            "text_or_null": None,
            "number_or_null": None,
            "text": "text",
            "number": 77,
        },
        {
            "text_or_null": None,
            "number_or_null": None,
            "text": "text",
            "number": "text",  # wrong format
        },
    ]

    errors = verify_records_schema(records, configured_catalog)

    assert not errors
