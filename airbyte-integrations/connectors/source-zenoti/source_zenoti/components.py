import datetime

from dataclasses import dataclass
from typing import Any, Mapping
from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor

@dataclass
class AppointmentsDatetimeBasedCursor(DatetimeBasedCursor):
  def _select_best_end_datetime(self) -> datetime.datetime:
    now = datetime.datetime.now(tz=self._timezone)
    if not self._end_datetime:
        return now
    return self._end_datetime.get_datetime(self.config)

  def _calculate_cursor_datetime_from_state(self, stream_state: Mapping[str, Any]) -> datetime.datetime:
    if self._cursor_field.eval(self.config, stream_state=stream_state) in stream_state:
      return datetime.datetime.now(tz=self._timezone)
    return datetime.datetime.min.replace(tzinfo=datetime.timezone.utc)
