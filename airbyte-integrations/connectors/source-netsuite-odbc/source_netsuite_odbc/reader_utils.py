
from typing import Final

NETSUITE_PAGINATION_INTERVAL: Final[int] = 10000

class NetsuiteODBCTableReader():
  def __init__(self, cursor, table_name, stream):
    self.cursor = cursor
    self.table_name = table_name
    self.properties = self.get_properties_from_stream(stream)
    self.primary_key = self.get_primary_key_from_stream(stream)
    self.incremental_column = self.get_incremental_column_from_stream(stream)

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
    table_state = self.read_state(state)
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
    incremental_column = f", {self.incremental_column} ASC" if self.incremental_column else ""
    query = f"SELECT TOP {NETSUITE_PAGINATION_INTERVAL} {values} FROM {self.table_name} WHERE ID > {table_state['last_id_seen']} ORDER BY {self.primary_key} ASC" + incremental_column
    # final_query = f"SELECT * FROM ({query}) WHERE ROWNUM < {NETSUITE_PAGINATION_INTERVAL}"
    return query
  
  def serialize_row_to_response(self, row):
    response = {}
    for i, column in enumerate(self.properties):
      response[column] = row[i]
    return response
  
  def read_state(self, state):
    table_state = state[self.table_name]
    print(table_state, len(table_state))
    if table_state is None or len(table_state) == 0:
      state[self.table_name] = {
        'last_id_seen': 0
      }
      return state[self.table_name]
    else:
      return table_state
    
  def update_state(self, state, results):
    last_id_seen = max((d[self.primary_key] for d in results if self.primary_key in d))
    table_state = state[self.table_name]
    table_state['last_id_seen'] = last_id_seen
    state[self.table_name] = table_state
    return state