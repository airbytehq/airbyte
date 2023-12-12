
from airbyte_cdk.models import (
    AirbyteStream,
)
import json
from typing import Iterable, Mapping, Any
from collections import defaultdict 


# See https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4407755805.html#SuiteAnalytics-Connect-System-Tables
# for descriptions of the system tables used
class NetsuiteODBCTableDiscoverer():
    def __init__(self, cursor):
        self.cursor = cursor
        self.data_type_switcher = {
          "SMALLINT":{"type": ["integer", "null"]},
          'BIGINT': {"type": ["integer", "null"]},
          'INTEGER': {"type": ["integer", "null"]},
          'VARCHAR': {"type": ["string", "null"]},
          "VARCHAR2":{"type": ["string", "null"]},
          "WVARCHAR": {"type": ["string", "null"]},
          "CHAR": {"type": ["string", "null"]},
          "CLOB": {"type": ["string", "null"]},
          "TIMESTAMP" : {"type": ["string", "null"], "format": "date-time"},
          "DOUBLE": {"type": ["number", "null"]},
        }

    def get_streams(self) -> Iterable[AirbyteStream]:
      tables = self.get_tables_with_join()
      primary_keys = self.find_primary_keys_bulk()
      for key in tables:
        table_values = tables[key]
        primary_key_for_table = primary_keys[key] if key in primary_keys else None
        yield self.get_table_stream_with_join(key, table_values, primary_key_for_table)

      
    def get_table_name(self, table: json) -> str:
       return table[0]

    
    def find_primary_keys_bulk(self):
      self.cursor.execute(f"SELECT pktable_name, pkcolumn_name FROM OA_FKEYS WHERE pktable_name is not NULL and pkcolumn_name IS NOT NULL")
      rows = self.cursor.fetchall()
      d = dict()
      for row in rows:
        d[row[0]] = row[1]
      return d
      
    def get_table_stream_with_join(self, table_name, table_columns, primary_key_column):
      # primary_key_column = []
      if primary_key_column is None:
        primary_key_column = []
      else:
        primary_key_column = [primary_key_column]

      properties = {}
      table_incremental_column = None
      for column in table_columns:
        if (self.is_column_incremental_join(column)):
          table_incremental_column = column['column_name']
        properties[column['column_name']] = column['column_type']
      
      json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": properties,
      }

      if table_incremental_column is not None:
        return AirbyteStream(name=table_name, json_schema=json_schema, supported_sync_modes=["full_refresh", "incremental"], source_defined_cursor=True, default_cursor_field=[table_incremental_column], primary_key=primary_key_column)
      else:
        return AirbyteStream(name=table_name, json_schema=json_schema, supported_sync_modes=["full_refresh"], primary_key=primary_key_column)

    def get_tables_with_join(self):
      self.cursor.execute("""
                          SELECT tab.table_name, tab.oa_userdata, col.column_name, col.type_name, col.oa_userdata
                          FROM OA_TABLES tab INNER JOIN OA_COLUMNS col ON col.table_name = tab.table_name
                          """)

      tables = []
      while True:
          row = self.cursor.fetchone()
          if not row:
              break
          processed_row = self.process_table_result(row)
          tables.append(processed_row)
      grouped_tables = self.group_results_by_table_name(tables)
      return grouped_tables
    
    def process_table_result(self, result):
      return {
        'table_name': result[0],
        'table_userdata': result[1],
        'column_name': result[2],
        'column_type': self.data_type_switcher[result[3]],
        'column_userdata': result[4]
      }
    
    def group_results_by_table_name(self, results):
      def default_value():
        return []
      d = defaultdict(default_value)
      for result in results:
        d[result['table_name']].append(result)
      return d

      
    def is_column_incremental_join(self, column) -> bool:
      column_meta_data = column['column_userdata']
      column_name = column['column_name']
      if (column_meta_data is not None and 'M-' in column_meta_data) or column_name in ['datelastmodified', 'lastmodified', 'lastmodifieddate']:
        return True
      else:
        return False