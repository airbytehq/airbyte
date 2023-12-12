#!/usr/bin/env python3
import sys
import os
import os

parent_dir_name = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# Add the ptdraft folder path to the sys.path list
sys.path.append(parent_dir_name)


from airbyte_cdk.models import (
    AirbyteStream,
)
import json
from typing import Iterable, Mapping, Any
from collections import defaultdict 
from odbc_utils import NetsuiteODBCCursorConstructor


# See https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4407755805.html#SuiteAnalytics-Connect-System-Tables
# for descriptions of the system tables used
class NetsuiteODBCTableDiscoverCacher():
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
      tables = self.get_tables()
      for table in tables:
        if self.is_table_custom(table): # skip custom tables because we'll handle them in the discover function
          continue
        yield self.get_table_stream(table)
      
    def get_table_name(self, table: json) -> str:
       return table[2]
    
    def is_table_custom(self, table):
      # query for custom table 
      # self.cursor.execute("SELECT TOP 1 * FROM OA_TABLES WHERE oa_userdata LIKE 'C%'")
      oa_data = table[5]
      if oa_data is None:
        return False
      return oa_data.startswith('C')

    def get_tables(self) -> list[Mapping[str, Any]]:
      self.cursor.execute("SELECT * FROM OA_TABLES")
      # self.cursor.execute("SELECT COUNT(*) FROM OA_TABLES WHERE oa_userdata IS NULL")
      tables = []
      while True:
          row = self.cursor.fetchone()
          print(row)
          if not row:
              break
          tables.append(row)
      return tables
    
    def get_table_stream(self, table: json) -> AirbyteStream:
      table_name = self.get_table_name(table)
      primary_key_column = self.find_primary_key_for_table(table)
      if primary_key_column is None:
        primary_key_column = []
      else:
        primary_key_column = [primary_key_column]

      properties = {}
      table_incremental_column = None
      columns = self.get_columns(table)
      for column in columns:
        if (self.is_column_custom(column)): # skip custom columns because we'll handle them in the discover() function
          continue
        is_incremental = self.is_column_incremental(column)
        if (is_incremental):
          table_incremental_column = self.get_column_name(column)
        properties[self.get_column_name(column)] = self.get_column_type(column)

      json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": properties,
      }

      is_incremental_table = table_incremental_column is not None

      result = {
        "json_schema": json_schema,
        "name": table_name,
        "supported_sync_modes": ["full_refresh", "incremental"] if is_incremental_table else ["full_refresh"],
        "source_defined_cursor": is_incremental_table,
        "default_cursor_field": [table_incremental_column] if is_incremental_table else [],
        "primary_key": primary_key_column,
      }

      return result
    
    def get_columns(self, table: json) -> Iterable[Mapping[str, Any]]:
      table_name = self.get_table_name(table)
      self.cursor.execute(f"SELECT table_name, column_name, type_name, oa_userdata FROM OA_COLUMNS WHERE TABLE_NAME = '{table_name}'")
      # self.cursor.execute(f"SELECT COUNT(*) FROM OA_COLUMNS WHERE oa_userdata LIKE 'C%'")

      while True:
        row = self.cursor.fetchone()
        # print(row)
        if not row:
          break
        yield row

    def is_column_custom(self, column):
      oa_userdata = column[3]
      if oa_userdata is None:
        return False
      return oa_userdata.startswith('C')

    def get_column_name(self, column: json) -> str:
      return column[1]
    
    def get_column_type(self, column: json) -> str:
      netsuite_data_type = column[2]
      return self.data_type_switcher[netsuite_data_type]
    
    def is_column_incremental(self, column: json) -> bool:
      column_meta_data = column[3]
      column_name = self.get_column_name(column)
      if (column_meta_data is not None and 'M-' in column_meta_data) or column_name in ['datelastmodified', 'lastmodified', 'lastmodifieddate']:
        return True
      else:
        return False
      
    def find_primary_key_for_table(self, table: json) -> str or None:
      table_name = self.get_table_name(table)
      self.cursor.execute(f"SELECT * FROM OA_FKEYS WHERE PKTABLE_NAME = '{table_name}'")
      row = self.cursor.fetchone()
      if row is None:
        return None
      return row[3] # return the column name for primary key


def read_config_from_secrets():
  parent_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
  parent_directory_of_parent = os.path.dirname(parent_directory)
  with open(parent_directory_of_parent + "/secrets/config.json") as fp:
    file_contents = fp.read()
    return json.loads(file_contents)

def print_to_file(schema):
  parent_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
  with open(parent_directory + f"/schemas/{schema['name']}.json", 'w') as fp:
    json.dump(schema, fp)
  print('done writing file')


def main():
    config_from_secrets = read_config_from_secrets()
    cursor_constructor = NetsuiteODBCCursorConstructor()
    cursor = cursor_constructor.create_database_cursor(config_from_secrets)
    discoverer = NetsuiteODBCTableDiscoverCacher(cursor)

    streams = discoverer.get_streams()

    for stream in streams:
      print(stream)
      print_to_file(stream)

if __name__ == "__main__":
    main()