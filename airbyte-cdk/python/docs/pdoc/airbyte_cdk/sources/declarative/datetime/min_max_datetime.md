Module airbyte_cdk.sources.declarative.datetime.min_max_datetime
================================================================

Classes
-------

`MinMaxDatetime(datetime: str, datetime_format: str = '', min_datetime: str = '', max_datetime: str = '')`
:   Compares the provided date against optional minimum or maximum times. If date is earlier than
    min_date, then min_date is returned. If date is greater than max_date, then max_date is returned.
    If neither, the input date is returned.

    ### Instance variables

    `datetime_format`
    :

    ### Methods

    `get_datetime(self, config, **kwargs) ‑> datetime.datetime`
    :