
import pytest

from source_netsuite_odbc.discover_utils import NetsuiteODBCTableDiscoverer
from airbyte_cdk.models import (
    SyncMode,
    AirbyteStream
)

@pytest.fixture
def joined_table_with_column():
  return ('Customer','SVMD------------|None', 'accountnumber','VARCHAR2', 'SV--------------|None')

@pytest.fixture
def joined_table_with_incremental_column():
  return ('Customer','SVMD------------|None', 'lastmodifieddate','TIMESTAMP', 'SVM-------------|None')



def test_processing_individual_column(joined_table_with_column):
  discoverer = NetsuiteODBCTableDiscoverer({})
  processed_table = discoverer.process_table_result(joined_table_with_column)
  assert processed_table == {
    'table_name': 'Customer',
    'table_userdata': 'SVMD------------|None',
    'column_name': 'accountnumber',
    'column_type': {'type': ['string', 'null']},
    'column_userdata': 'SV--------------|None'
  }

def test_processing_incremental_column(joined_table_with_column, joined_table_with_incremental_column):
  discoverer = NetsuiteODBCTableDiscoverer({})
  processed_table = discoverer.process_table_result(joined_table_with_column)
  assert discoverer.is_column_incremental(processed_table) == False

  processed_incremental_table = discoverer.process_table_result(joined_table_with_incremental_column)
  assert discoverer.is_column_incremental(processed_incremental_table) == True



def test_creating_table_stream_single_column(joined_table_with_column):

  discoverer = NetsuiteODBCTableDiscoverer({})
  processed_table = discoverer.process_table_result(joined_table_with_column)
  stream = discoverer.get_table_stream_with_join('Customer', [processed_table], ['id'])

  expected_json_schema = {'$schema': 'http://json-schema.org/draft-07/schema#', 'type': 'object', 'properties': {'accountnumber': {'type': ['string', 'null']}}}
  expected_stream = AirbyteStream(name='Customer', json_schema=expected_json_schema, supported_sync_modes=[SyncMode.full_refresh], source_defined_cursor=None, default_cursor_field=None, source_defined_primary_key=None, namespace=None, primary_key=['id'])

  assert stream == expected_stream


def test_creating_table_stream_multi_column(monkeypatch, joined_table_with_column, joined_table_with_incremental_column):

  discoverer = NetsuiteODBCTableDiscoverer({})
  processed_table = discoverer.process_table_result(joined_table_with_column)
  processed_table_incremental = discoverer.process_table_result(joined_table_with_incremental_column)
  stream = discoverer.get_table_stream_with_join('Customer', [processed_table, processed_table_incremental], ['id'])

  expected_json_schema = {'$schema': 'http://json-schema.org/draft-07/schema#', 'type': 'object', 'properties': {'accountnumber': {'type': ['string', 'null']}, 'lastmodifieddate': {'type': ['string', 'null'], 'format': 'date-time'}}}
  expected_stream = AirbyteStream(name='Customer', json_schema=expected_json_schema, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental], source_defined_cursor=True, default_cursor_field=['lastmodifieddate'], source_defined_primary_key=None, namespace=None, primary_key=['id'])

  assert stream == expected_stream