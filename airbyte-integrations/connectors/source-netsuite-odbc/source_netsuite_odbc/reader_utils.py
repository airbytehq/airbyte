
from typing import Final
from datetime import datetime

NETSUITE_PAGINATION_INTERVAL: Final[int] = 10000

class NetsuiteODBCTableReader():
  def __init__(self, cursor, table_name, stream, is_incremental):
    self.cursor = cursor
    self.table_name = table_name
    self.properties = self.get_properties_from_stream(stream)
    self.primary_key = self.get_primary_key_from_stream(stream)
    self.incremental_column = self.get_incremental_column_from_stream(stream)
    self.is_incremental_stream = is_incremental

  def get_primary_key_from_stream(self, stream):
    key = stream.primary_key
    if not key:
      return "id"
    else:
      return key[0]
  
  def get_incremental_column_from_stream(self, stream):
    cursor_field = stream.default_cursor_field
    if not cursor_field:
      return None
    else:
      return cursor_field[0]

  def get_properties_from_stream(self, stream):
    return stream.json_schema['properties'].keys()
  
  def read_table(self, state):
    table_state = self.read_state(state) # state includes last_id_seen and last_date_updated (incremental only)
    self.cursor.execute(self.generate_ordered_query(table_state))
    rows = []
    while True:
      row = self.cursor.fetchone()
      if not row:
        break
      # print(row)
      rows.append(self.serialize_row_to_response(row))
    return rows
  
  def generate_ordered_query(self, table_state):
    values = ', '.join(self.properties) # we use values instead of '*' because we want to preserve the order of the columns
    incremental_column_sorter = f", {self.incremental_column} ASC" if self.incremental_column else ""
    incremental_column_filter = f" AND {self.incremental_column} > {table_state['last_date_updated']}" if self.is_incremental_stream else ""
    query = f"""
      SELECT TOP {NETSUITE_PAGINATION_INTERVAL} {values} FROM {self.table_name} 
      WHERE ID > {table_state['last_id_seen']} {incremental_column_filter}
      ORDER BY {self.primary_key} 
      ASC""" + incremental_column_sorter
    return query
  
  def serialize_row_to_response(self, row):
    response = {}
    for i, column in enumerate(self.properties):
      response[column] = row[i]
    return response
  
  def read_state(self, state):
    table_state = state[self.table_name]
    if table_state is None or len(table_state) == 0:
      state[self.table_name] = {
        'last_id_seen': 0,
        'last_date_updated': None
      }
      return state[self.table_name]
    else:
      return table_state
    
  def update_state(self, state, results):
    last_id_seen = max((d[self.primary_key] for d in results if self.primary_key in d))
    most_recent_date = self.find_most_recent_date(results)
    table_state = state[self.table_name]
    table_state['last_id_seen'] = last_id_seen
    table_state['last_date_updated'] = most_recent_date
    state[self.table_name] = table_state
    return state
  
  def find_most_recent_date(self, results):
    incremental_values = [result[self.incremental_column] for result in results if self.incremental_column in result]
    return max(incremental_values).isoformat(timespec='seconds')