from unittest.mock import MagicMock
from airbyte_cdk.sources.declarative.schema import FirstRecordSchemaLoader

FIRST_RECORD = {'id': 'abcd1234', 'label': 'user-viewer-role', 'description': 'user-viewer-role', 'created': '2023-06-28T17:39:34.000Z', 'lastUpdated': '2023-06-28T17:39:34.000Z', '_links': {'permissions': {'href': 'https://abcd-admin.okta.com/api/v1/iam/roles/role12345/permissions'}, 'self': {'href': 'https://abcd-admin.okta.com/api/v1/iam/roles/role12345'}}}
EXPECTED_SCHEMA = {'$schema': 'http://json-schema.org/schema#', 'additionalProperties': True, 'properties': {'id': {'type': ['string', 'null']}, 'label': {'type': ['string', 'null']}, 'description': {'type': ['string', 'null']}, 'created': {'type': ['string', 'null'], 'format': 'date-time'}, 'lastUpdated': {'type': ['string', 'null'], 'format': 'date-time'}, '_links': {'properties': {'permissions': {'properties': {'href': {'type': ['string', 'null']}}, 'type': ['object', 'null']}, 'self': {'properties': {'href': {'type': ['string', 'null']}}, 'type': ['object', 'null']}}, 'type': ['object', 'null']}}, 'type': 'object'}

def test_first_record_schema_loader():
    iterator = MagicMock()
    iterator.__next__.return_value = FIRST_RECORD

    retriever = MagicMock()
    retriever.read_records.return_value = iterator

    first_record_schema_loader = FirstRecordSchemaLoader(retriever=retriever)
    assert first_record_schema_loader.get_json_schema() == EXPECTED_SCHEMA
