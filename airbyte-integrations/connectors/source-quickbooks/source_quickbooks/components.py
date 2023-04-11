#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
import typing
from collections import abc
from dataclasses import dataclass

import dpath.util
from airbyte_cdk.sources.declarative.incremental import DatetimeBasedCursor
from airbyte_cdk.sources.declarative.types import Record, StreamSlice


class LastRecordDictProxy(abc.MutableMapping):
    """
    Patch a dict object to be able to get/set/delete/etc... values by path.
    Example:
        >>> record = LastRecordDictProxy({"root": {"nested": "value"}})
        >>> record["root/nested"]
        <<< "value"
        >>> record.get("root/nested")
        <<< "value"
    """

    def __init__(self, record: Record, field_mapping: typing.Mapping = None):
        self._record: Record = record
        self._field_mapping = field_mapping if field_mapping is not None else {}

    def __setitem__(self, k: str, v: typing.Any) -> None:
        dpath.util.set(self._record, k, v)

    def __delitem__(self, v: str) -> None:
        dpath.util.delete(self._record, v)

    def __getitem__(self, k: str) -> typing.Any:
        try:
            return dpath.util.get(self._record, k)
        except KeyError as e:
            if k in self._field_mapping:
                return dpath.util.get(self._record, self._field_mapping[k])
            raise e

    def __len__(self) -> int:
        return len(self._record)

    def __iter__(self) -> typing.Iterator:
        return self._record

    def __bool__(self):
        return bool(self._record)


@dataclass
class CustomDatetimeBasedCursor(DatetimeBasedCursor):
    """
    This class is used to override the default DatetimeBasedCursor behavior in the way the cursor values from the `last_record` are
    retrieved, specifically the nested values. In case the last_record looks like follows, there is no way we can get the nested cursor
    value for now by means of the base class.
    {
      "id": "id",
      "Metadata": {
        "LastUpdatedTime": "<DateTime>"
      }
    }
    To adopt this change to the LowCode CDK, this issue was created - https://github.com/airbytehq/airbyte/issues/25008.
    """

    def update_cursor(self, stream_slice: StreamSlice, last_record: typing.Optional[Record] = None):
        super(CustomDatetimeBasedCursor, self).update_cursor(
            stream_slice=stream_slice,
            last_record=LastRecordDictProxy(last_record, {self.cursor_field.eval(self.config): "MetaData/LastUpdatedTime"}),
        )

    def _format_datetime(self, dt: datetime.datetime):
        return dt.isoformat("T", "seconds")

    def parse_date(self, date: str) -> datetime.datetime:
        return datetime.datetime.strptime(date, self.datetime_format).astimezone(self._timezone)
