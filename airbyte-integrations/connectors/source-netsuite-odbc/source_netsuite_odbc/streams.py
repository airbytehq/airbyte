
from airbyte_cdk.sources.streams import Stream, IncrementalMixin
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Union, Final
from airbyte_cdk.models import AirbyteMessage, AirbyteStream, SyncMode
from datetime import date
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteStateMessage,
    Type,
    AirbyteStateType,
    AirbyteStreamState,
    StreamDescriptor,
    FailureType,
)
import pyodbc
from airbyte_cdk.utils.traced_exception import AirbyteTracedException
from dateutil import parser
from .errors import NETSUITE_CONNECTION_EXPIRED_FAILURE
from .odbc_utils import NetsuiteODBCCursorConstructor

# A stream's read method can return one of the following types:
# Mapping[str, Any]: The content of an AirbyteRecordMessage
# AirbyteMessage: An AirbyteMessage. Could be of any type
StreamData = Union[Mapping[str, Any], AirbyteMessage]

NETSUITE_PAGINATION_INTERVAL: Final[int] = 10
EARLIEST_DATE: Final[str] = date(2020, 1, 1)
YEARS_FORWARD_LOOKING: Final[int] = 1
# Sometimes, system created accounts can have primary key values < 0.  To be safe, we choose
# an arbitrary value of -10000 as the starting value for our primary key
STARTING_PRIMARY_KEY_VALUE: Final[int] = -10000

GENERATING_INCREMENTAL_QUERY_WITH_NO_INCREMENTAL_COLUMN_ERROR: Final[str] = "We should not be generating an incremental query unless an incremental column exists."


class NetsuiteODBCStream(Stream):

    #  The functions before the init call are all used to initialize the stream
    def get_primary_key_from_airbyte_stream(self, stream: AirbyteStream):
      key = stream.primary_key
      if not key:
        return []
      else:
        return sorted(key, reverse=True)
  
    def get_incremental_column_from_airbyte_stream(self, stream: AirbyteStream):
      cursor_field = stream.default_cursor_field
      if not cursor_field:
        return None
      elif len(cursor_field) > 1:
        raise Exception('Assumption Broken: Incremental Column should always be a top level field.  Instead, we\'re receiving a sub-field as an incremental column.')
      else:
        return cursor_field[0]

    def get_properties_from_stream(self, stream):
      return stream.json_schema['properties'].keys()
    
    def set_up_primary_key_last_value_seen(self, primary_key):
      primary_key_last_value_seen = {}
      for key in primary_key:
        primary_key_last_value_seen[key] = STARTING_PRIMARY_KEY_VALUE
      return primary_key_last_value_seen

    def __init__(self, db_connection: pyodbc.Cursor, table_name, stream, config):
      self.db_connection = db_connection
      self.table_name = table_name
      self.properties = self.get_properties_from_stream(stream)
      self.primary_key_column = self.get_primary_key_from_airbyte_stream(stream)
      self.incremental_column = self.get_incremental_column_from_airbyte_stream(stream)
      self.primary_key_last_value_seen = self.set_up_primary_key_last_value_seen(self.primary_key_column)
      self.incremental_most_recent_value_seen = None
      self.json_schema = stream.json_schema
      self.config = config # used for restoring the connection when it expires

    def read_records(
      self,
      sync_mode: SyncMode,
      cursor_field: Optional[List[str]] = None,
      stream_slice: Optional[Mapping[str, Any]] = None,
      stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
      try:
        self.process_stream_state(stream_state)
        self.db_connection.execute(self.generate_query(sync_mode, stream_slice))
        number_records = 0
        while True:
          row = self.db_connection.fetchone()
          if not row and number_records < NETSUITE_PAGINATION_INTERVAL:
            break
          # if number of rows >= page limit, we need to fetch another page
          elif not row:
            self.logger.info(f"Fetching another page for the stream {self.table_name}.  Current state is (primary key: {str(self.primary_key_last_value_seen)}, date: {self.incremental_most_recent_value_seen}")
            number_records = 0
            self.db_connection.execute(self.generate_query(sync_mode, stream_slice))
            continue
          # data from netsuite does not include columns, so we need to assign each value to the correct column name
          serialized_data = self.serialize_row_to_response(row)
          # before we yield record, update state
          self.update_last_values_seen(serialized_data, sync_mode)
          self.find_most_recent_date(serialized_data)
          number_records = number_records + 1
          #yield response
          yield serialized_data
      except Exception as e:
        message = str(e)
        if NETSUITE_CONNECTION_EXPIRED_FAILURE in message:
          self.logger.info(f"Connection expired for stream {self.table_name}.  Reconnecting...")
          cursor_constructor = NetsuiteODBCCursorConstructor()
          new_db_connection = cursor_constructor.create_database_connection(self.config)
          self.db_connection = new_db_connection
          current_stream_state = self.get_updated_state(stream_state, {})
          self.read_records(sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=current_stream_state)
        else:
          raise e
      self.logger.info(f"Finished Stream Slice for Netsuite ODBC Table {self.table_name} with stream slice: {stream_slice}")

    #  STATE MANAGEMENT FUNCTIONS
    def process_stream_state(self, stream_state):
      if stream_state is None:
        return
      if 'last_date_updated' in stream_state:
        self.incremental_most_recent_value_seen = stream_state['last_date_updated']
      if 'last_values_seen' in stream_state:
        self.primary_key_last_value_seen = stream_state['last_values_seen']

    def find_most_recent_date(self, result):
      if self.incremental_column is None:
        return
      date_value_received = None
      if self.incremental_column in result:
        date_value_received = result[self.incremental_column]
      if date_value_received is not None:
        if self.incremental_most_recent_value_seen is None:
          self.incremental_most_recent_value_seen = date_value_received
        else:
          self.incremental_most_recent_value_seen = max(self.incremental_most_recent_value_seen, date_value_received)

    def update_last_values_seen(self, result, sync_mode: SyncMode):
      if self.primary_key_column is None:
        return
      for key in self.primary_key_column:
        # we don't check for max() because netsuite primary key columns are incrementing.
        # if we checked for max, we'd need to deal with key sequence
        if key in result:
          self.primary_key_last_value_seen[key] = result[key]
        else:
          raise Exception('A primary key column was not found in the result. Please make sure your properties include all primary key columns.')
        
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

    def get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]) -> Mapping[str, Any]:
      if 'last_date_updated' in current_stream_state and self.incremental_most_recent_value_seen is not None:
        last_date_updated = max(current_stream_state['last_date_updated'], self.incremental_most_recent_value_seen)
      else:
        last_date_updated = self.incremental_most_recent_value_seen
      if 'last_values_seen' in current_stream_state:
        last_values_seen = self.update_last_values_seen_from_current_stream_state(current_stream_state)
      else:
        last_values_seen = self.primary_key_last_value_seen

      return {
        'last_values_seen': last_values_seen,
        'last_date_updated': last_date_updated
      }
    
    def update_last_values_seen_from_current_stream_state(self, current_stream_state: MutableMapping[str, Any]):
      stream_last_values = current_stream_state['last_values_seen']
      new_values = {}
      for key in self.primary_key_column:
        stream_value = stream_last_values[key] if key in stream_last_values else STARTING_PRIMARY_KEY_VALUE
        non_stream_value = self.primary_key_last_value_seen[key] if key in self.primary_key_last_value_seen else STARTING_PRIMARY_KEY_VALUE
        new_values[key] = max(stream_value, non_stream_value)
      return new_values

    # END STATE MANAGEMENT FUNCTIONS

    # QUERY GENERATION FUNCTIONS
    def has_composite_primary_key(self):
      return len(self.primary_key_column) > 1
    
    def generate_query(self, sync_mode, stream_slice):
      if sync_mode == SyncMode.full_refresh:
        return self.generate_full_refresh_query(stream_slice)
      elif sync_mode == SyncMode.incremental:
        return self.generate_incremental_query(stream_slice)
      else:
        raise Exception(f'Unsupported Sync Mode: {sync_mode}.  Please use either "full_refresh" or "incremental"')

    # How does full refresh work?
    # We first split things into stream slices.  Then, we start with filtering our SQL query by > the start date of the stream slice
    # and <= the end date of the stream slice.  We then sort by the primary key column (s).
    #  As we fetch records, we start filtering by > the most recent primary key value we've seen.  Because primary keys 
    # can be composite, we need to handle the cases where the first column might have multiple rows for a single value (since the second
    # or third row might have different values)
    # Note:  Outside of the stream slice dates, we don't filter by dates in full refresh.  We instead rely on Netsuite's ids being incremental.
    def generate_full_refresh_query(self, stream_slice):
      values = ', '.join(self.properties) # we use values instead of '*' because we want to preserve the order of the columns
      incremental_column_sorter = f", {self.incremental_column} ASC" if self.incremental_column else ""
      # per https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_156257805177.html#subsect_156330163819
      # date literals need to be wrapped in a to_date function
      incremental_column_filter = f"{self.incremental_column} >= to_timestamp('{stream_slice['first_day']}', 'YYYY-MM-DD') AND {self.incremental_column} <= to_timestamp('{stream_slice['last_day']}', 'YYYY-MM-DD')" if self.incremental_column else ""
      primary_key_filter = self.generate_primary_key_filter()
      primary_key_sorter = self.generate_primary_key_sorter()
      and_connector = " AND " if primary_key_filter != "" and incremental_column_filter != "" else ""
      where_clause = "WHERE " if primary_key_filter != "" or incremental_column_filter != "" else ""
      query = f"""
        SELECT TOP {NETSUITE_PAGINATION_INTERVAL} {values} FROM {self.table_name} 
        {where_clause}{primary_key_filter}{and_connector}{incremental_column_filter}
        ORDER BY {primary_key_sorter}""" + incremental_column_sorter
      return query
    
    def generate_primary_key_filter(self):
      primary_key_filter = ""
      # primary keys can be composite!  To deal with this, we add filters for each column
      # This is an edge case.  In the standard case where there's only a single primary key column, 
      # this could should only add a single filter
      for key in self.primary_key_column:
        last_value_seen = self.primary_key_last_value_seen[key] if key in self.primary_key_last_value_seen else STARTING_PRIMARY_KEY_VALUE
        if primary_key_filter != "":
          primary_key_filter = primary_key_filter + " AND "
        if primary_key_filter == "" and self.has_composite_primary_key():
          primary_key_filter = primary_key_filter + f"{key} = {last_value_seen}"
        else:
          primary_key_filter = primary_key_filter + f"{key} > {last_value_seen}"
      # if it's a composite key, we add a second column to try to "upgrade" to the next column value
      # if we don't do this, we don't properly make our way up the table
      # NOTE:  This only works when there are two columns in the primary key
      if self.has_composite_primary_key():
        first_column = self.primary_key_column[0]
        first_column_value = self.primary_key_last_value_seen[first_column] if first_column in self.primary_key_last_value_seen else STARTING_PRIMARY_KEY_VALUE
        primary_key_filter = primary_key_filter + f" OR {first_column} > {first_column_value}"
      return primary_key_filter
    
    def generate_primary_key_sorter(self):
      primary_key_sorter = ""
      for key in self.primary_key_column:
        if primary_key_sorter != "":
          primary_key_sorter = primary_key_sorter + ", "
        primary_key_sorter = primary_key_sorter + f"{key} ASC"
      return primary_key_sorter
    
    # How does Incremental Refresh work?
    # We first split things into stream slices.  Then, we start with filtering our SQL query by > the start date of the stream slice
    # and <= the end date of the stream slice.  We then sort by the incremental column, and then by the primary key column (s).
    #  As we fetch records, we start filtering by > the most recent incremental time we've seen. We also add on a filter for 
    # = the most recent incremental time but with a primary key > the last one we've seen.  This ensures that we don't miss any records
    # in the case where page size = N and there are N + 1 records with the same incremental time. 
    def generate_incremental_query(self, stream_slice):
      if self.incremental_column is None:
        raise AirbyteTracedException.from_exception(message=GENERATING_INCREMENTAL_QUERY_WITH_NO_INCREMENTAL_COLUMN_ERROR, failure_type=FailureType.system_error)
      values = ', '.join(self.properties) # we use values instead of '*' because we want to preserve the order of the columns
      incremental_column_sorter = f"{self.incremental_column} ASC" if self.incremental_column else ""
      incremental_filter = self.generate_incremental_filter_for_incremental_refresh(stream_slice)
      primary_key_filter = self.generate_primary_key_filter_for_incremental_refresh(stream_slice)
      primary_key_sorter = self.generate_primary_key_sorter()
      query = f"""
        SELECT TOP {NETSUITE_PAGINATION_INTERVAL} {values} FROM {self.table_name}
        WHERE {incremental_filter} OR {primary_key_filter}
        ORDER BY {incremental_column_sorter}, {primary_key_sorter}
      """
      print(query)
      return query
    
    def generate_primary_key_filter_for_incremental_refresh(self, stream_slice):
      primary_key_filter = self.generate_primary_key_filter()
      starting_timestamp = self.incremental_most_recent_value_seen if self.incremental_most_recent_value_seen is not None else stream_slice['first_day']
      starting_timestamp = parser.parse(str(starting_timestamp)).strftime('%Y-%m-%d %H:%M:%S.%f')
      return f"({self.incremental_column} = to_timestamp('{starting_timestamp}', 'YYYY-MM-DD HH24:MI:SS.FF') AND {primary_key_filter})"
    
    def generate_incremental_filter_for_incremental_refresh(self, stream_slice):
      # per https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_156257805177.html#subsect_156330163819
      # date literals need to be wrapped in a to_date function
      if self.incremental_column is None:
        raise AirbyteTracedException.from_exception(message=GENERATING_INCREMENTAL_QUERY_WITH_NO_INCREMENTAL_COLUMN_ERROR, failure_type=FailureType.system_error)
      starting_timestamp = self.incremental_most_recent_value_seen if self.incremental_most_recent_value_seen is not None else stream_slice['first_day']
      starting_timestamp = parser.parse(str(starting_timestamp)).strftime('%Y-%m-%d %H:%M:%S.%f')
      ending_timestamp = parser.parse(str(stream_slice['last_day'])).strftime('%Y-%m-%d %H:%M:%S.%f')
      return f"({self.incremental_column} > to_timestamp('{starting_timestamp}', 'YYYY-MM-DD HH24:MI:SS.FF') AND {self.incremental_column} <= to_timestamp('{ending_timestamp}', 'YYYY-MM-DD HH24:MI:SS.FF'))"
    
    # END QUERY GENERATION FUNCTIONS
  
    def serialize_row_to_response(self, row):
      response = {}
      for i, column in enumerate(self.properties):
        response[column] = row[i]
      return response

    # STREAM SLICE FUNCTIONS

    def stream_slices(
      self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
      # return [{'first_day': date(2000, 1, 1), 'last_day': date(2023, 12,31)}]
      start_date, end_date = self.get_range_to_fetch(sync_mode=sync_mode, stream_state=stream_state)

      # Ensure start_date is before end_date
      if start_date > end_date:
        start_date, end_date = end_date, start_date

      current_date = start_date
      date_slices = []
      while current_date <= end_date:
        date_slices.append(self.get_slice_for_year(current_date))
        current_date = current_date.replace(year=current_date.year + 1, month=1)

      return date_slices
    
    def get_range_to_fetch(self, sync_mode: SyncMode, stream_state: Optional[Mapping[str, Any]] = None):
      end_slice_range = date.today()
      # we fetch data for some years in the future because accountants can book transactions in the future
      end_slice_range = end_slice_range.replace(year=end_slice_range.year + YEARS_FORWARD_LOOKING, day=1) 
      # we use an earliest date of 1980 since 1998 was when netsuite was founded.  Note that in some cases customers might have ported over older historical data
      start_slice_range = EARLIEST_DATE
      if sync_mode == SyncMode.incremental:
        incremental_date = date.fromisoformat(stream_state['last_date_updated']) if 'last_date_updated' in stream_state else EARLIEST_DATE
        start_slice_range = incremental_date
      elif not (sync_mode == SyncMode.full_refresh):
        raise Exception(f'Unsupported Sync Mode: {sync_mode}.  Please use either "full_refresh" or "incremental"')
      return start_slice_range, end_slice_range
    
    def get_slice_for_year(self, date_for_slice: date):
      year_to_use = date_for_slice.year
      first_day = date(year_to_use, 1, 1)
      last_day = date(year_to_use, 12, 31)
      return {'first_day': first_day, 'last_day': last_day}
    
    # END STREAM SLICE FUNCTIONS

    # DEFINE PROPERTIES
    @property
    def name(self) -> str:
      return self.table_name
  
    @property
    def cursor_field(self) -> Union[str, List[str]]:
      return self.incremental_column

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
      return self.primary_key_column
    
    def supports_incremental(self) -> bool:
      """
      :return: True if this stream supports incrementally reading data
      """
      if self._wrapped_cursor_field() is None:
        return False
      return len(self._wrapped_cursor_field()) > 0

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.
        """
        return self.json_schema
