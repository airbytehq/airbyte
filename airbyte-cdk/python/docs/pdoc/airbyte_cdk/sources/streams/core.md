Module airbyte_cdk.sources.streams.core
=======================================

Functions
---------

    
`package_name_from_class(cls: object) ‑> str`
:   Find the package name given a class name

Classes
-------

`IncrementalMixin()`
:   Mixin to make stream incremental.
    
    class IncrementalStream(Stream, IncrementalMixin):
        @property
        def state(self):
            return self._state
    
        @state.setter
        def state(self, value):
            self._state[self.cursor_field] = value[self.cursor_field]

    ### Ancestors (in MRO)

    * abc.ABC

    ### Instance variables

    `state: MutableMapping[str, Any]`
    :   State getter, should return state in form that can serialized to a string and send to the output
        as a STATE AirbyteMessage.
        
        A good example of a state is a cursor_value:
            {
                self.cursor_field: "cursor_value"
            }
        
         State should try to be as small as possible but at the same time descriptive enough to restore
         syncing process from the point where it stopped.

`Stream()`
:   Base abstract class for an Airbyte Stream. Makes no assumption of the Stream's underlying transport protocol.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.declarative_stream.DeclarativeStream
    * airbyte_cdk.sources.streams.http.http.HttpStream

    ### Class variables

    `transformer: airbyte_cdk.sources.utils.transform.TypeTransformer`
    :

    ### Instance variables

    `cursor_field: Union[str, List[str]]`
    :   Override to return the default cursor field used by this stream e.g: an API entity might always use created_at as the cursor field.
        :return: The name of the field used as a cursor. If the cursor is nested, return an array consisting of the path to the cursor.

    `logger`
    :

    `name: str`
    :   :return: Stream name. By default this is the implementing class name, but it can be overridden as needed.

    `namespace: Optional[str]`
    :   Override to return the namespace of this stream, e.g. the Postgres schema which this stream will emit records for.
        :return: A string containing the name of the namespace.

    `primary_key: Union[str, List[str], List[List[str]], ForwardRef(None)]`
    :   :return: string if single primary key, list of strings if composite primary key, list of list of strings if composite primary key consisting of nested fields.
          If the stream has no primary keys, return None.

    `source_defined_cursor: bool`
    :   Return False if the cursor can be configured by the user.

    `state_checkpoint_interval: Optional[int]`
    :   Decides how often to checkpoint state (i.e: emit a STATE message). E.g: if this returns a value of 100, then state is persisted after reading
        100 records, then 200, 300, etc.. A good default value is 1000 although your mileage may vary depending on the underlying data source.
        
        Checkpointing a stream avoids re-reading records in the case a sync is failed or cancelled.
        
        return None if state should not be checkpointed e.g: because records returned from the underlying data source are not returned in
        ascending order with respect to the cursor field. This can happen if the source does not support reading records in ascending order of
        created_at date (or whatever the cursor is). In those cases, state must only be saved once the full stream has been read.

    `supports_incremental: bool`
    :   :return: True if this stream supports incrementally reading data

    ### Methods

    `as_airbyte_stream(self) ‑> airbyte_cdk.models.airbyte_protocol.AirbyteStream`
    :

    `get_error_display_message(self, exception: BaseException) ‑> Optional[str]`
    :   Retrieves the user-friendly display message that corresponds to an exception.
        This will be called when encountering an exception while reading records from the stream, and used to build the AirbyteTraceMessage.
        
        The default implementation of this method does not return user-friendly messages for any exception type, but it should be overriden as needed.
        
        :param exception: The exception that was raised
        :return: A user-friendly message that indicates the cause of the error

    `get_json_schema(self) ‑> Mapping[str, Any]`
    :   :return: A dict of the JSON schema representing this stream.
        
        The default implementation of this method looks for a JSONSchema file with the same name as this stream's "name" property.
        Override as needed.

    `get_updated_state(self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any])`
    :   Override to extract state from the latest record. Needed to implement incremental sync.
        
        Inspects the latest record extracted from the data source and the current state object and return an updated state object.
        
        For example: if the state object is based on created_at timestamp, and the current state is {'created_at': 10}, and the latest_record is
        {'name': 'octavia', 'created_at': 20 } then this method would return {'created_at': 20} to indicate state should be updated to this object.
        
        :param current_stream_state: The stream's current state object
        :param latest_record: The latest record extracted from the stream
        :return: An updated state object

    `read_records(self, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) ‑> Iterable[Mapping[str, Any]]`
    :   This method should be overridden by subclasses to read records based on the inputs

    `stream_slices(self, *, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, cursor_field: List[str] = None, stream_state: Mapping[str, Any] = None) ‑> Iterable[Optional[Mapping[str, Any]]]`
    :   Override to define the slices for this stream. See the stream slicing section of the docs for more information.
        
        :param sync_mode:
        :param cursor_field:
        :param stream_state:
        :return: