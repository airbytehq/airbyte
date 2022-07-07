Module airbyte_cdk.sources.declarative.stream_slicers.substream_slicer
======================================================================

Classes
-------

`SubstreamSlicer(parent_streams: List[airbyte_cdk.sources.streams.core.Stream], state: airbyte_cdk.sources.declarative.states.dict_state.DictState, slice_definition: Mapping[str, Any])`
:   Stream slicer that iterates over the parent's stream slices and records and emits slices by interpolating the slice_definition mapping
    Will populate the state with `parent_stream_slice` and `parent_record` so they can be accessed by other components

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.stream_slicers.stream_slicer.StreamSlicer
    * abc.ABC

    ### Methods

    `stream_slices(self, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, stream_state: Mapping[str, Any]) ‑> Iterable[Mapping[str, Any]]`
    :   Iterate over each parent stream.
        For each stream, iterate over its stream_slices.
        For each stream slice, iterate over each records.
        yield a stream slice for each such records.
        
        If a parent slice contains no record, emit a slice with parent_record=None.
        
        The template string can interpolate the following values:
        - parent_stream_slice: mapping representing the parent's stream slice
        - parent_record: mapping representing the parent record
        - parent_stream_name: string representing the parent stream name