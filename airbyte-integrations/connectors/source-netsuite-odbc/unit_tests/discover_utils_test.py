
import pytest

from source_netsuite_odbc.discover_utils import NetsuiteODBCTableDiscoverer
from airbyte_cdk.models import (
    SyncMode,
    AirbyteStream
)

@pytest.fixture
def single_column():
  return ('Customer', 'accountnumber','VARCHAR2', 'SV--------------|None')


@pytest.fixture
def incremental_column_without_name():
  return ('Customer', 'differentName', 'TIMESTAMP', 'SVM-------------|None')

@pytest.fixture
def incremental_column_with_name():
  return ('Customer', 'lastmodifieddate','TIMESTAMP', 'SV--------------|None')

@pytest.fixture
def table_row():
  return ('Customer','SVMD------------|None')

@pytest.fixture
def multiple_columns():
  return [
    ('Customer', 'accountnumber','VARCHAR2', 'SV--------------|None'),
    ('Customer', 'acquisitionsource','BIGINT', 'SV--D-----------|SuiteCommerce Analytics Data'),
    ('Customer', 'alcoholrecipienttype','VARCHAR2','SV--D-----------|None'),
    ('Customer', 'altemail','VARCHAR2', 'SV--------------|Is A Business'),
    ('Customer', 'altname','VARCHAR2', 'SV--------------|None'),
    ('Customer', 'altphone','VARCHAR2', 'SV--------------|None'),
    ('Customer', 'assignedwebsite','BIGINT', 'SV--D-----------|None'),
    ('Customer', 'lastmodifieddate','TIMESTAMP', 'SVM-------------|None')
  ]

def mock_pk_result(self, table):
  return 'id'


def test_processing_individual_column(single_column, incremental_column_with_name):
  discoverer = NetsuiteODBCTableDiscoverer({})
  assert discoverer.get_column_name(single_column) == 'accountnumber'
  assert discoverer.get_column_type(single_column) == {"type": ["string", "null"]}
  assert discoverer.get_column_type(incremental_column_with_name) == {"type": ["string", "null"], "format": "date-time"}

def test_processing_incremental_column(single_column, incremental_column_with_name, incremental_column_without_name):
  discoverer = NetsuiteODBCTableDiscoverer({})
  assert not discoverer.is_column_incremental(single_column)
  assert discoverer.is_column_incremental(incremental_column_with_name)
  assert discoverer.is_column_incremental(incremental_column_without_name)



def test_creating_table_stream_single_column(monkeypatch, single_column, table_row):
  def mock_single_column(self, table):
    return [single_column]

  # We need to mock the find primary key function as otherwise it hits the database
  monkeypatch.setattr(NetsuiteODBCTableDiscoverer, "find_primary_key_for_table", mock_pk_result)
  # similarly, get_columns makes an ODBC call
  monkeypatch.setattr(NetsuiteODBCTableDiscoverer, "get_columns", mock_single_column)


  discoverer = NetsuiteODBCTableDiscoverer({})
  stream = discoverer.get_table_stream(table_row)

  expected_json_schema = {'$schema': 'http://json-schema.org/draft-07/schema#', 'type': 'object', 'properties': {'accountnumber': {'type': ['string', 'null']}}}
  expected_stream = AirbyteStream(name='Customer', json_schema=expected_json_schema, supported_sync_modes=[SyncMode.full_refresh], source_defined_cursor=None, default_cursor_field=None, source_defined_primary_key=None, namespace=None, primary_key=['id'])

  assert stream == expected_stream


def test_creating_table_stream_multi_column(monkeypatch, multiple_columns, table_row):
  def mock_multiple_column(self, table):
    return multiple_columns

  # We need to mock the find primary key function as otherwise it hits the database
  monkeypatch.setattr(NetsuiteODBCTableDiscoverer, "find_primary_key_for_table", mock_pk_result)
  # similarly, get_columns makes an ODBC call
  monkeypatch.setattr(NetsuiteODBCTableDiscoverer, "get_columns", mock_multiple_column)


  discoverer = NetsuiteODBCTableDiscoverer({})
  stream = discoverer.get_table_stream(table_row)

  expected_json_schema = {'$schema': 'http://json-schema.org/draft-07/schema#', 'type': 'object', 'properties': {'accountnumber': {'type': ['string', 'null']}, 'acquisitionsource': {'type': ['integer', 'null']}, 'alcoholrecipienttype': {'type': ['string', 'null']}, 'altemail': {'type': ['string', 'null']}, 'altname': {'type': ['string', 'null']}, 'altphone': {'type': ['string', 'null']}, 'assignedwebsite': {'type': ['integer', 'null']}, 'lastmodifieddate': {'type': ['string', 'null'], 'format': 'date-time'}}}
  expected_stream = AirbyteStream(name='Customer', json_schema=expected_json_schema, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental], source_defined_cursor=True, default_cursor_field=['lastmodifieddate'], source_defined_primary_key=None, namespace=None, primary_key=['id'])

  assert stream == expected_stream