
from airbyte_cdk.models import (
    AirbyteStream,
)
import json

# See https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4407755805.html#SuiteAnalytics-Connect-System-Tables
# for descriptions of the system tables used
class NetsuiteODBCTableDiscoverer():
    def __init__(self, cursor):
        self.cursor = cursor
        self.tables = []
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

    def get_streams(self) -> list[AirbyteStream]:
      self.get_tables()
      streams = []
      for table in self.tables:
        streams.append(self.get_table_stream(table))
      return streams

    def get_table_name(self, table: json) -> str:
       return table[2]

    def get_tables(self) -> None:
      self.cursor.execute("SELECT * FROM OA_TABLES")
      while True:
          row = self.cursor.fetchone()
          if not row:
              break
          self.tables.append(row)
   
    def get_table_stream(self, table: json) -> AirbyteStream:
      table_name = self.get_table_name(table)
      columns = self.get_columns(table)
      primary_key_column = self.find_primary_key_for_table(table)
      if primary_key_column is None:
        primary_key_column = []
      else:
        primary_key_column = [primary_key_column]


      properties = {}
      table_incremental_column = None
      for column in columns:
        is_incremental = self.is_column_incremental(column)
        if (is_incremental):
          table_incremental_column = self.get_column_name(column)
        properties[self.get_column_name(column)] = self.get_column_type(column)

      json_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": properties,
      }

      if table_incremental_column is not None:
        return AirbyteStream(name=table_name, json_schema=json_schema, supported_sync_modes=["full_refresh", "incremental"], source_defined_cursor=True, default_cursor_field=[table_incremental_column], primary_key=primary_key_column)
      else:
        return AirbyteStream(name=table_name, json_schema=json_schema, supported_sync_modes=["full_refresh"], primary_key=primary_key_column)
    
    def get_columns(self, table: json):
      table_name = self.get_table_name(table)
      self.cursor.execute(f"SELECT * FROM OA_COLUMNS WHERE TABLE_NAME = '{table_name}'")
      columns = []
      while True:
        row = self.cursor.fetchone()
        if not row:
          break
        columns.append(row)
      return columns
    
    def get_column_name(self, column: json) -> str:
      return column[3]
    
    def get_column_type(self, column: json) -> str:
      netsuite_data_type = column[5]
      return self.data_type_switcher[netsuite_data_type]
    
    def is_column_incremental(self, column: json) -> bool:
      column_meta_data = column[12]
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

    