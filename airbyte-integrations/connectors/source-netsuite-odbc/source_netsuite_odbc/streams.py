
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union, Final, String
from airbyte_cdk.models import AirbyteMessage, AirbyteStream, SyncMode
from datetime import datetime
import calendar

# A stream's read method can return one of the following types:
# Mapping[str, Any]: The content of an AirbyteRecordMessage
# AirbyteMessage: An AirbyteMessage. Could be of any type
StreamData = Union[Mapping[str, Any], AirbyteMessage]

NETSUITE_PAGINATION_INTERVAL: Final[int] = 10000
EARLIEST_DATE: Final[str] = datetime(1980, 1, 1)
YEARS_FORWARD_LOOKING: Final[int] = 1
STARTING_CURSOR_VALUE: Final[int] = -1



class NetsuiteODBCStream(Stream, IncrementalMixin):
    def get_primary_key_from_stream(self, stream):
      key = stream.primary_key
      if not key:
        return "id"
      elif len(key) > 1:
        raise Exception('Assumption Broken: Primary Key should always be a top level field.  Instead, we\'re receiving a sub-field as a primary key.')
      else:
        return key[0]
  
    def get_incremental_column_from_stream(self, stream):
      cursor_field = stream.default_cursor_field
      if not cursor_field:
        return None
      elif len(cursor_field) > 1:
        raise Exception('Assumption Broken: Incremental Column should always be a top level field.  Instead, we\'re receiving a sub-field as an incremental column.')
      else:
        return cursor_field[0]

    def get_properties_from_stream(self, stream):
      return stream.json_schema['properties'].keys()

    def __init__(self, cursor, table_name, stream, is_incremental):
      self.cursor = cursor
      self.table_name = table_name
      self.properties = self.get_properties_from_stream(stream)
      self.primary_key = self.get_primary_key_from_stream(stream)
      self.incremental_column = self.get_incremental_column_from_stream(stream)
      self.is_incremental_stream = is_incremental
      self.cursor_value_last_id_seen = STARTING_CURSOR_VALUE
      self.incremental_most_recent_value_seen = None

    @property
    def name(self) -> str:
      """
      :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.
      """
      return self.table_name
  
  
    @property
    def cursor_field(self) -> Union[str, List[str]]:
      """
      Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
      :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.
      """
      return [self.incremental_column]

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
      """
      :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
        If the stream has no primary keys, return None.
      """
      return [self.primary_key]


    def read_records(
      self,
      sync_mode: SyncMode,
      cursor_field: Optional[List[str]] = None,
      stream_slice: Optional[Mapping[str, Any]] = None,
      stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
      self.cursor.execute(self.generate_ordered_query(stream_state, stream_slice))
      while True:
        row = self.cursor.fetchone()
        if not row:
          break
        # data from netsuite does not include columns, so we need to assign each value to the correct column name
        serialized_data = self.serialize_row_to_response(row)
        # before we yield record, update state
        if self.primary_key in serialized_data:
          self.cursor_value_last_id_seen = max(self.cursor_value_last_id_seen, serialized_data[self.primary_key])
        if self.incremental_column in serialized_data:
          self.incremental_most_recent_value_seen = max(self.incremental_most_recent_value_seen, serialized_data[self.incremental_column])
        #yield response
        yield serialized_data
  
    def generate_ordered_query(self, table_state, stream_slice):
      values = ', '.join(self.properties) # we use values instead of '*' because we want to preserve the order of the columns
      incremental_column_sorter = f", {self.incremental_column} ASC" if self.incremental_column else ""
      incremental_column_filter = f" AND {self.incremental_column} >= {stream_slice['first_day']} AND {self.incremental_column} < {stream_slice['last_day']}"
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

    def stream_slices(
      self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
      start_date, end_date = self.get_range_to_fetch(sync_mode=sync_mode, stream_state=stream_state)

      # Ensure start_date is before end_date
      if start_date > end_date:
        start_date, end_date = end_date, start_date

      current_date = start_date
      date_slices = []
      while current_date <= end_date:
        date_slices.append(self.get_slice_for_month(current_date))
        # Increment month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)

      return date_slices
    
    def get_range_to_fetch(self, sync_mode: SyncMode, stream_state: Optional[Mapping[str, Any]] = None):
      end_slice_range = datetime.now()
      # we fetch data for some years in the future because accountants can book transactions in the future
      end_slice_range = end_slice_range.replace(year=end_slice_range.year + YEARS_FORWARD_LOOKING) 
      # we use an earliest date of 1980 since 1998 was when netsuite was founded.  Note that in some cases customers might have ported over older historical data
      start_slice_range = EARLIEST_DATE
      if sync_mode == 'incremental':
        start_slice_range = datetime.fromisoformat(stream_state['last_date_updated'])
      elif not (sync_mode == 'full_refresh'):
        raise Exception(f'Unsupported Sync Mode: {sync_mode}.  Please use either "full_refresh" or "incremental"')
      return start_slice_range, end_slice_range
    
    def get_slice_for_month(self, date: datetime):
      first_day = datetime(date.year, date.month, 1)
      days_in_month = calendar.monthrange(date.year, date.month)[1]
      last_day = datetime(date.year, date.month, days_in_month)
      return {'first_day': first_day.isoformat(timespec='seconds'), 'last_day': last_day.isoformat(timespec='seconds')}
    
    @property
    def state_checkpoint_interval(self) -> Optional[int]:
      """
      Decides how often to checkpoint state (i.e: emit a STATE message). E.g: if this returns a value of 100, then state is persisted after reading
      100 records, then 200, 300, etc.. A good default value is 1000 although your mileage may vary depending on the underlying data source.

      Checkpointing a stream avoids re-reading records in the case a sync is failed or cancelled.

      We return state after 10,000 records because that is how large of a page we can return from Netsuite in
      a sustainable way, and we should be able to restart successfully after each page.
      """
      return 10000
    
    @property
    def state(self) -> MutableMapping[str, Any]:
      """State getter, should return state in form that can serialized to a string and send to the output
      as a STATE AirbyteMessage.
      """
      return {
        'last_id_seen': self.cursor_value_last_id_seen,
        'last_date_updated': self.incremental_most_recent_value_seen,
      }

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
      """State setter, accept state serialized by state getter."""
      last_id_seen = value['last_id_seen']
      if not last_id_seen:
        self.cursor_value_last_id_seen = STARTING_CURSOR_VALUE
      else:
        self.cursor_value_last_id_seen = value['last_id_seen']
      self.incremental_most_recent_value_seen = value['last_date_updated']
