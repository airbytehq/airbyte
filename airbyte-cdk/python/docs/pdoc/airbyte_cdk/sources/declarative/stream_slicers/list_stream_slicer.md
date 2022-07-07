Module airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer
========================================================================

Classes
-------

`ListStreamSlicer(slice_values: Union[str, List[str]], slice_definition: Mapping[str, Any], config: Mapping[str, Any])`
:   Stream slicer that iterates over the values of a list
    If slice_values is a string, then evaluate it as literal and assert the resulting literal is a list

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.stream_slicers.stream_slicer.StreamSlicer
    * abc.ABC

    ### Methods

    `stream_slices(self, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, stream_state: Mapping[str, Any]) ‑> Iterable[Mapping[str, Any]]`
    :