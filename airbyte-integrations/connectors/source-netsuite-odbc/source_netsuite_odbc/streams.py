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

NETSUITE_PAGINATION_INTERVAL: Final[int] = 10000
YEARS_FORWARD_LOOKING: Final[int] = 1
# Sometimes, system created accounts can have primary key values < 0.  To be safe, we choose
# an arbitrary value of -10000 as the starting value for our primary key
STARTING_PRIMARY_KEY_VALUE: Final[int] = -10000

GENERATING_INCREMENTAL_QUERY_WITH_NO_INCREMENTAL_COLUMN_ERROR: Final[
    str
] = "We should not be generating an incremental query unless an incremental column exists."


class NetsuiteODBCStream(Stream):
    #  The functions before the init call are all used to initialize the stream
    def get_primary_key_from_airbyte_stream(self, stream: AirbyteStream):
        key = stream.primary_key
        if not key:
            return []
        elif stream.name == "TransactionAccountingLine":
            # we have this special case because the "transactionline" column on the TransactionAccountingLine table does not actually support WHERE clauses for some reason
            # therefore, we knowingly accept duplicate rows in order to try to fetch all rows.
            return ["transaction", "accountingbook"]
        else:
            return sorted(key, reverse=True)

    def get_incremental_column_from_airbyte_stream(self, stream: AirbyteStream):
        cursor_field = stream.default_cursor_field
        if not cursor_field:
            return None
        elif len(cursor_field) > 1:
            raise Exception(
                "Assumption Broken: Incremental Column should always be a top level field.  Instead, we're receiving a sub-field as an incremental column."
            )
        else:
            return cursor_field[0]

    def get_properties_from_stream(self, stream):
        return stream.json_schema["properties"].keys()

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
        self.config = config  # used for restoring the connection when it expires

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        try:
            self.process_input_stream_state(stream_state)
            self.db_connection.execute(self.generate_query(stream_slice))
            number_records = 0
            while True:
                row = self.db_connection.fetchone()
                if not row and number_records < NETSUITE_PAGINATION_INTERVAL:
                    # if number of rows < page limit, we've reached the end of the stream slice
                    break
                elif not row:
                    # if number of rows >= page limit, we need to fetch another page
                    self.logger.info(
                        f"Fetching another page for the stream {self.table_name}.  Current state is (primary key: {str(self.primary_key_last_value_seen)}, date: {self.incremental_most_recent_value_seen}"
                    )
                    number_records = 0
                    self.db_connection.execute(self.generate_query(stream_slice))
                    continue
                # data from netsuite does not include columns, so we need to assign each value to the correct column name
                serialized_data = self.serialize_row_to_response(row)
                # before we yield record, update state
                self.update_last_values_seen(serialized_data)
                self.find_most_recent_date(serialized_data)
                number_records = number_records + 1
                yield serialized_data
        except Exception as e:
            message = str(e)
            if NETSUITE_CONNECTION_EXPIRED_FAILURE in message:
                self.logger.info(f"Connection expired for stream {self.table_name}.  Reconnecting...")
                cursor_constructor = NetsuiteODBCCursorConstructor()
                new_db_connection = cursor_constructor.create_database_connection(self.config)
                self.db_connection = new_db_connection
                current_stream_state = self.get_updated_state(stream_state, {})
                self.read_records(
                    sync_mode=sync_mode, cursor_field=cursor_field, stream_slice=stream_slice, stream_state=current_stream_state
                )
            else:
                raise e
        self.logger.info(f"Finished Stream Slice for Netsuite ODBC Table {self.table_name} with stream slice: {stream_slice}")
        #  Because the WHERE filter changes in each stream slice, primary key values are not guaranteed to be in order
        #  across stream slives.  Therefore, we reset the primary key last value seen after each stream slice
        #  Also, we set incremental last value seen to None at the start of a stream to set state to start of stream slice
        if self.incremental_column is not None:  #  if an incremental column does not exist, we do NOT reset the primary key
            self.primary_key_last_value_seen = self.set_up_primary_key_last_value_seen(self.primary_key_column)
            self.incremental_most_recent_value_seen = None
        self.db_connection.execute("SELECT COUNT(*) FROM " + self.table_name)
        self.logger.info(
            f"Finished reading stream slice for {self.table_name}.  Total number of records in table: {self.db_connection.fetchone()[0]}"
        )

    #  STATE MANAGEMENT FUNCTIONS
    def process_input_stream_state(self, stream_state):
        if stream_state is None:
            return
        if "last_date_updated" in stream_state:
            self.incremental_most_recent_value_seen = stream_state["last_date_updated"]
        if "last_values_seen" in stream_state:
            self.primary_key_last_value_seen = stream_state["last_values_seen"]

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

    def update_last_values_seen(self, result):
        if self.primary_key_column is None:
            return
        for key in self.primary_key_column:
            # we don't check for max() because netsuite primary key columns are incrementing.
            # if we checked for max, we'd need to deal with key sequence
            if key in result:
                self.primary_key_last_value_seen[key] = result[key]
            else:
                raise Exception(
                    "A primary key column was not found in the result. Please make sure your properties include all primary key columns."
                )

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
        if (
            current_stream_state is not None
            and "last_date_updated" in current_stream_state
            and self.incremental_most_recent_value_seen is not None
        ):
            last_date_updated = max(current_stream_state["last_date_updated"], self.incremental_most_recent_value_seen)
        else:
            last_date_updated = self.incremental_most_recent_value_seen
        if current_stream_state is not None and "last_values_seen" in current_stream_state:
            last_values_seen = self.update_last_values_seen_from_current_stream_state(current_stream_state)
        else:
            last_values_seen = self.primary_key_last_value_seen

        return {"last_values_seen": last_values_seen, "last_date_updated": last_date_updated}

    def update_last_values_seen_from_current_stream_state(self, current_stream_state: MutableMapping[str, Any]):
        stream_last_values = current_stream_state["last_values_seen"]
        new_values = {}
        for key in self.primary_key_column:
            stream_value = stream_last_values[key] if key in stream_last_values else STARTING_PRIMARY_KEY_VALUE
            non_stream_value = (
                self.primary_key_last_value_seen[key] if key in self.primary_key_last_value_seen else STARTING_PRIMARY_KEY_VALUE
            )
            new_values[key] = max(stream_value, non_stream_value)
        return new_values

    # END STATE MANAGEMENT FUNCTIONS

    # QUERY GENERATION FUNCTIONS
    def has_composite_primary_key(self):
        return len(self.primary_key_column) > 1

    def generate_query(self, stream_slice):
        if self.incremental_column is not None:
            return self.generate_query_with_incremental(stream_slice)
        else:
            return self.generate_query_with_no_incremental(stream_slice)

    # How does full refresh work?
    # We first split things into stream slices.  Then, we start with filtering our SQL query by >= the start date of the stream slice
    # and <= the end date of the stream slice.  We then sort by the primary key column (s).
    #  As we fetch records, we start filtering by > the most recent primary key value we've seen.  Because primary keys
    # can be composite, we need to handle the cases where the first column might have multiple rows for a single value (since the second
    # or third row might have different values)
    # Note:  Outside of the stream slice dates, we don't filter by dates in full refresh.  We instead rely on Netsuite's ids being incremental.
    # example Query:
    # SELECT TOP 10000 [every property is individually articulated, like  accountnumber, acquisitionsource, alcoholrecipienttype ...] FROM Customer
    #    WHERE ((id > -10000)) AND lastmodifieddate >= to_timestamp('2025-01-01', 'YYYY-MM-DD') AND lastmodifieddate <= to_timestamp('2025-12-31', 'YYYY-MM-DD')
    #    ORDER BY id ASC, lastmodifieddate ASC
    def generate_query_with_no_incremental(self, stream_slice):
        values = ", ".join(self.properties)  # we use values instead of '*' because we want to preserve the order of the columns
        # per https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_156257805177.html#subsect_156330163819
        # date literals need to be wrapped in a to_date function
        primary_key_filter = self.generate_primary_key_filter()
        primary_key_sorter = self.generate_primary_key_sorter()
        where_clause = "WHERE " if primary_key_filter != "" else ""
        query = f"""
        SELECT TOP {NETSUITE_PAGINATION_INTERVAL} {values} FROM {self.table_name} 
        {where_clause}{primary_key_filter}
        ORDER BY {primary_key_sorter}"""
        return query

    def generate_primary_key_filter(self):
        # Note that netsuite tables can have composite primary keys, and we've so far
        # seen keys with up to 3 columns.
        # To deal with this, we use generic syntax for keysort pagination with composite keys
        # https://stackoverflow.com/questions/56719611/generic-sql-predicate-to-use-for-keyset-pagination-on-multiple-fields
        # given n keys, we should end up with (n1 > val1) OR (n1 = val1 AND n2 > val2) OR (n1 = val1 AND n2 = val2 AND n3 > val3) OR ...
        filter_string = ""
        for i, key in enumerate(self.primary_key_column):
            last_value_seen = (
                self.primary_key_last_value_seen[key] if key in self.primary_key_last_value_seen else STARTING_PRIMARY_KEY_VALUE
            )
            filters = [f"{key} > {last_value_seen}"]
            for j in range(i):
                previous_key = self.primary_key_column[j]
                previous_value = (
                    self.primary_key_last_value_seen[previous_key]
                    if previous_key in self.primary_key_last_value_seen
                    else STARTING_PRIMARY_KEY_VALUE
                )
                filters.append(f"{previous_key} = {previous_value}")
            filter_string_for_step = "(" + " AND ".join(filters) + ")"
            if filter_string != "":
                filter_string = filter_string + " OR " + filter_string_for_step
            else:
                filter_string = filter_string_for_step
        return f"({filter_string})"

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
    # example Query:
    # SELECT TOP 10000 [every property is individually articulated, like  accountnumber, acquisitionsource, alcoholrecipienttype ...] FROM Customer
    #    WHERE (lastmodifieddate > to_timestamp('2023-12-05 19:13:52.000000', 'YYYY-MM-DD HH24:MI:SS.FF') AND lastmodifieddate <= to_timestamp('2025-12-31 00:00:00.000000', 'YYYY-MM-DD HH24:MI:SS.FF')) OR (lastmodifieddate = to_timestamp('2023-12-05 19:13:52.000000', 'YYYY-MM-DD HH24:MI:SS.FF') AND ((id > 1152)))
    #    ORDER BY lastmodifieddate ASC, id ASC
    def generate_query_with_incremental(self, stream_slice):
        if self.incremental_column is None:
            raise AirbyteTracedException(
                message=GENERATING_INCREMENTAL_QUERY_WITH_NO_INCREMENTAL_COLUMN_ERROR, failure_type=FailureType.system_error
            )
        values = ", ".join(self.properties)  # we use values instead of '*' because we want to preserve the order of the columns
        incremental_column_sorter = f"{self.incremental_column} ASC" if self.incremental_column else ""
        incremental_filter = self.generate_incremental_filter_for_incremental_refresh(stream_slice)
        primary_key_filter = self.generate_primary_key_filter_for_incremental_refresh(stream_slice)
        primary_key_sorter = self.generate_primary_key_sorter()
        query = f"""
        SELECT TOP {NETSUITE_PAGINATION_INTERVAL} {values} FROM {self.table_name}
        WHERE {incremental_filter} OR {primary_key_filter}
        ORDER BY {incremental_column_sorter}, {primary_key_sorter}
      """
        return query

    def generate_primary_key_filter_for_incremental_refresh(self, stream_slice):
        primary_key_filter = self.generate_primary_key_filter()
        starting_timestamp = (
            self.incremental_most_recent_value_seen if self.incremental_most_recent_value_seen is not None else stream_slice["first_day"]
        )
        if starting_timestamp is not None:
            starting_timestamp = parser.parse(str(starting_timestamp)).strftime("%Y-%m-%d %H:%M:%S.%f")
            timestamp_filter = f"{self.incremental_column} = to_timestamp('{starting_timestamp}', 'YYYY-MM-DD HH24:MI:SS.FF')"
        else:
            timestamp_filter = f"{self.incremental_column} IS NULL"
        return f"({timestamp_filter} AND {primary_key_filter})"

    def generate_incremental_filter_for_incremental_refresh(self, stream_slice):
        if self.incremental_column is None:
            raise AirbyteTracedException.from_exception(
                message=GENERATING_INCREMENTAL_QUERY_WITH_NO_INCREMENTAL_COLUMN_ERROR, failure_type=FailureType.system_error
            )
        # first, we check to see if we've been given a null slice, and if so, we change the query accordingly
        # To understand why we need a null slice, see the comment in stream_slices()
        if stream_slice["first_day"] is None or stream_slice["last_day"] is None:
            return f"{self.incremental_column} IS NULL"
        # per https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_156257805177.html#subsect_156330163819
        # date literals need to be wrapped in a to_date function
        starting_timestamp = (
            self.incremental_most_recent_value_seen if self.incremental_most_recent_value_seen is not None else stream_slice["first_day"]
        )
        starting_timestamp = parser.parse(str(starting_timestamp)).strftime("%Y-%m-%d %H:%M:%S.%f")
        ending_timestamp = parser.parse(str(stream_slice["last_day"])).strftime("%Y-%m-%d %H:%M:%S.%f")
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
        start_date, end_date = self.get_range_to_fetch(sync_mode=sync_mode, stream_state=stream_state)

        # Ensure start_date is before end_date
        if start_date > end_date:
            return []

        current_date = start_date
        date_slices = []
        while current_date <= end_date:
            date_slices.append(self.get_slice_for_year(current_date))
            current_date = current_date.replace(year=current_date.year + 1, month=1)

        # If date slices exist, we add a null slice to the end of the list.
        # We do this because while common sense would suggest that a incremental column would not be nullable,
        # Netsuite obeys no such rules.  Since incremental columns can be null, we need to fetch for this, which we do by adding a null slice.
        date_slices.append(self.get_null_slice())

        return date_slices

    def get_null_slice(self):
        return {"first_day": None, "last_day": None}

    def get_range_to_fetch(self, sync_mode: SyncMode, stream_state: Optional[Mapping[str, Any]] = None):
        end_slice_range = date.today()
        # we fetch data for some years in the future because accountants can book transactions in the future
        end_slice_range = end_slice_range.replace(year=end_slice_range.year + YEARS_FORWARD_LOOKING, day=1, month=12)
        # we use an earliest date of 1980 since 1998 was when netsuite was founded.  Note that in some cases customers might have ported over older historical data
        start_slice_range = self.get_earliest_date()
        if sync_mode == SyncMode.incremental:
            incremental_date = (
                date.fromisoformat(stream_state["last_date_updated"]) if "last_date_updated" in stream_state else start_slice_range
            )
            start_slice_range = incremental_date
        elif not (sync_mode == SyncMode.full_refresh):
            raise Exception(f'Unsupported Sync Mode: {sync_mode}.  Please use either "full_refresh" or "incremental"')
        return start_slice_range, end_slice_range

    def get_earliest_date(self):
        starting_year = int(self.config.get("starting_year", "1980"))
        return date(starting_year, 1, 1)

    def get_slice_for_year(self, date_for_slice: date):
        year_to_use = date_for_slice.year
        first_day = date(year_to_use, 1, 1)
        last_day = date(year_to_use, 12, 31)
        return {"first_day": first_day, "last_day": last_day}

    # END STREAM SLICE FUNCTIONS

    # DEFINE PROPERTIES
    @property
    def name(self) -> str:
        return self.table_name

    @property
    def cursor_field(self) -> Union[str, List[str]]:
        if self.incremental_column is None:
          return []
        else:     
            return self.incremental_column

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self.primary_key_column

    def supports_incremental(self) -> bool:
        """
        :return: True if this stream supports incrementally reading data
        """
        if self.cursor_field() is None:
            return False
        return len(self._wrapped_cursor_field()) > 0

    def get_json_schema(self) -> Mapping[str, Any]:
        """
        :return: A dict of the JSON schema representing this stream.
        """
        return self.json_schema
