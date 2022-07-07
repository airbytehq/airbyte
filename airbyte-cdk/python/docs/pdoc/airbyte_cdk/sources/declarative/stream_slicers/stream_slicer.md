Module airbyte_cdk.sources.declarative.stream_slicers.stream_slicer
===================================================================

Classes
-------

`StreamSlicer()`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * abc.ABC

    ### Descendants

    * airbyte_cdk.sources.declarative.stream_slicers.cartesian_product_stream_slicer.CartesianProductStreamSlicer
    * airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer.DatetimeStreamSlicer
    * airbyte_cdk.sources.declarative.stream_slicers.list_stream_slicer.ListStreamSlicer
    * airbyte_cdk.sources.declarative.stream_slicers.single_slice.SingleSlice
    * airbyte_cdk.sources.declarative.stream_slicers.substream_slicer.SubstreamSlicer

    ### Methods

    `stream_slices(self, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, stream_state: Mapping[str, Any]) ‑> Iterable[Mapping[str, Any]]`
    :