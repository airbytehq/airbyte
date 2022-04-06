#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.models import AirbyteMessage, Type
import jsonschema
from source_faker import SourceFaker

# TODO: airbyte/airbyte-integrations/connectors/source-faker/.venv/lib/python3.9/site-packages/airbyte_cdk/sources/utils/transform.py:12: DeprecationWarning: Call to deprecated class AirbyteLogger. (Use logging.getLogger('airbyte') instead) -- Deprecated since version 0.1.47.

# TODO: We don't have dict-with-indifferent-access in Python, so we need to make a better catalog object.  This is probably a bad idea.
class LazyConfigDict(dict):
    def __getattr__(self, attr):
        return self[attr]
    def __setattr__(self, attr, value):
        self[attr] = value

def test_source_streams():
    source = SourceFaker()
    config = {"count": 1}
    catalog = source.discover(None, config)
    catalog = AirbyteMessage(type=Type.CATALOG, catalog=catalog).dict(exclude_unset=True)
    schemas = [stream["json_schema"] for stream in catalog["catalog"]["streams"]]

    assert len(schemas) == 1
    assert schemas[0]['properties'] == {
        "id": {"type": "number"},
        "created_at": {"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"},
        "updated_at":{"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"},
        "job": {"type": "string"},
        "company": {"type": "string"},
        "ssn": {"type": "string"},
        "residence": {"type": "string"},
        "current_location": {"type": "array", "items": "number"},
        "blood_group": {"type": "string"},
        "website": {"type": "array", "items": "string"},
        "username": {"type": "string"},
        "name": {"type": "string"},
        "sex": {"type": "string"},
        "address": {"type": "string"},
        "mail": {"type": "string"},
        "birthdate": {"type": "string", "format": "date"},
    }

    # TODO: `jsonschema.exceptions.SchemaError: 'string' is not valid under any of the given schemas`... But, I think this is valid?
    # for schema in schemas:
    #     jsonschema.Draft7Validator.check_schema(schema)

def test_read_random_data ():
    source = SourceFaker()
    logger = None
    config = { "count": 10 }
    catalog = LazyConfigDict({"streams": [LazyConfigDict({"stream": LazyConfigDict({"name": "Users"})})]})
    state = {}
    iterator = source.read(logger, config, catalog, state)

    record_rows_count = 0
    state_rows_count = 0
    for row in iterator:
        if row.type is Type.RECORD: #TODO: Python seems to really overload the "IS" operator, is this the right way to do this?
            record_rows_count = record_rows_count + 1
        if row.type is Type.STATE:
            state_rows_count = state_rows_count + 1

    assert record_rows_count == 10
    assert state_rows_count == 1

def test_read_with_seed ():
    """
    This test asserts that setting a seed always returns the same values
    """

    source = SourceFaker()
    logger = None
    config = { "count": 1, "seed": 100 }
    catalog = LazyConfigDict({"streams": [LazyConfigDict({"stream": LazyConfigDict({"name": "Users"})})]})
    state = {}
    iterator = source.read(logger, config, catalog, state)

    # TODO: In JS, I could find the record with a map... what's the pythonic way to do this?  How can I set record's type ahead of time?
    record = None
    for row in iterator:
        if row.type is Type.RECORD:
            record = row

    assert record.record.data['company'] == 'Gibson-Townsend'
    assert record.record.data['mail'] == 'zamoradenise@yahoo.com'
