import datetime

from dataclasses import dataclass
from airbyte_cdk.sources.declarative.incremental.datetime_based_cursor import DatetimeBasedCursor

@dataclass
class AppointmentsDatetimeBasedCursor(DatetimeBasedCursor):
  def _select_best_end_datetime(self) -> datetime.datetime:
    now = datetime.datetime.now(tz=self._timezone)
    if not self._end_datetime:
        return now
    return self._end_datetime.get_datetime(self.config)
