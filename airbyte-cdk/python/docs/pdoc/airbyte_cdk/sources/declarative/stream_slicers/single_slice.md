Module airbyte_cdk.sources.declarative.stream_slicers.single_slice
==================================================================

Classes
-------

`SingleSlice(**kwargs)`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.stream_slicers.stream_slicer.StreamSlicer
    * abc.ABC

    ### Methods

    `stream_slices(self, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, stream_state: Mapping[str, Any]) ‑> Iterable[Mapping[str, Any]]`
    :