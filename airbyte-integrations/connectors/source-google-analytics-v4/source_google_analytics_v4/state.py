#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import pendulum


class StreamStateProxy(dict):
    """
    docstring
    """

    DATE_FORMAT = "%Y-%m-%d"

    @classmethod
    def str_to_dt(cls, _str):
        return _str and pendulum.parse(_str).date()

    @classmethod
    def dt_to_str(cls, dt):
        return dt and dt.strftime(cls.DATE_FORMAT)

    @property
    def non_golden_dates(self):
        return list(map(self.str_to_dt, self.get("non_golden_dates", [])))

    @property
    def golden_date(self):
        return self.str_to_dt(self.get("golden_date") or self.get("ga_date"))  # support legacy format

    @golden_date.setter
    def golden_date(self, val):
        self["golden_date"] = self.dt_to_str(val)

    def non_golden_date_sequences(self, max_length):
        seq_start, seq_end = None, None
        today = pendulum.now().date()
        for current_day in self.non_golden_dates:
            if current_day > today:
                continue
            if seq_start is None:
                seq_start = seq_end = current_day
                continue
            next_day = seq_end.add(days=1)
            if current_day != next_day:
                # sequence broken
                yield [seq_start, seq_end]
                seq_start, seq_end = None, None
                continue
            seq_end = current_day
            if (seq_end - seq_start).days == max_length:
                yield [seq_start, seq_end]
                seq_start, seq_end = None, None
                continue
        if seq_start and seq_end:
            yield [seq_start, seq_end]

    def update_with_record(self, date, is_data_golden):
        date = self.str_to_dt(date)
        if is_data_golden:
            if date in self.non_golden_dates:
                self.non_golden_dates.remove(date)
            self.golden_date = max(self.golden_date, date) if self.golden_date else date
        if not is_data_golden:
            self.non_golden_dates.append(date)
            self.non_golden_dates.sort()
            if self.golden_date and self.golden_date < date:
                self.golden_date = None
        # record_date, record_golden =
        # if current_stream_state
        #     current_date, current_golden = current_stream_state.get(self.cursor_field, ["", False])
        # return {self.cursor_field: max(, )}
