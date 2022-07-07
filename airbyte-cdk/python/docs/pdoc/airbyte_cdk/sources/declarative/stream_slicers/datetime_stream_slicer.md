Module airbyte_cdk.sources.declarative.stream_slicers.datetime_stream_slicer
============================================================================

Classes
-------

`DatetimeStreamSlicer(start_datetime: airbyte_cdk.sources.declarative.datetime.min_max_datetime.MinMaxDatetime, end_datetime: airbyte_cdk.sources.declarative.datetime.min_max_datetime.MinMaxDatetime, step: str, cursor_value: Union[str, airbyte_cdk.sources.declarative.interpolation.interpolated_string.InterpolatedString], datetime_format: str, config: Mapping[str, Any])`
:   Helper class that provides a standard way to create an ABC using
    inheritance.

    ### Ancestors (in MRO)

    * airbyte_cdk.sources.declarative.stream_slicers.stream_slicer.StreamSlicer
    * abc.ABC

    ### Class variables

    `timedelta_regex`
    :

    ### Methods

    `is_int(self, s) ‑> bool`
    :

    `parse_date(self, date: Any) ‑> <module 'datetime' from '/opt/homebrew/Cellar/python@3.9/3.9.12/Frameworks/Python.framework/Versions/3.9/lib/python3.9/datetime.py'>`
    :

    `stream_slices(self, sync_mode: airbyte_cdk.models.airbyte_protocol.SyncMode, stream_state: Mapping[str, Any]) ‑> Iterable[Mapping[str, Any]]`
    :