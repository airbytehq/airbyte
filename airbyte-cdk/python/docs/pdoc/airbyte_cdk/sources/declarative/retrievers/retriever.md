Module airbyte_cdk.sources.declarative.retrievers.retriever
===========================================================

Classes
-------

`Retriever()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.retrievers.simple_retriever.SimpleRetriever

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

    ### Methods

    `read_records(self, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None, stream_state: Mapping[str, Any] = None) ‑> Iterable[Mapping[str, Any]]`
    :

    `stream_slices(self, *, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, stream_state: Mapping[str, Any] = None) ‑> Iterable[Optional[Mapping[str, Any]]]`
    :