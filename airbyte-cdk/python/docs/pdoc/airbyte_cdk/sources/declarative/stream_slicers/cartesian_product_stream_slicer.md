Module airbyte_cdk.sources.declarative.stream_slicers.cartesian_product_stream_slicer
=====================================================================================

Classes
-------

`CartesianProductStreamSlicer(stream_slicers: List[airbyte_cdk.sources.declarative.stream_slicers.stream_slicer.StreamSlicer])`
:   Stream slicers that iterates over the cartesian product of input stream slicers
    Given 2 stream slicers with the following slices:
    A: [{"i": 0}, {"i": 1}, {"i": 2}]
    B: [{"s": "hello"}, {"s": "world"}]
    the resulting stream slices are
    [
        {"i": 0, "s": "hello"},
        {"i": 0, "s": "world"},
        {"i": 1, "s": "hello"},
        {"i": 1, "s": "world"},
        {"i": 2, "s": "hello"},
        {"i": 2, "s": "world"},
    ]

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.stream_slicers.stream_slicer.StreamSlicer
    * abc.ABC

    ### Methods

    `stream_slices(self, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, stream_state: Mapping[str, Any]) ‑> Iterable[Mapping[str, Any]]`
    :