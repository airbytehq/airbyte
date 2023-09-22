#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from multiprocessing import current_process
from random import choice
from threading import Lock
from typing import Any, Dict, List, Mapping, Set

from airbyte_cdk.models import AirbyteRecordMessage, Type
from mimesis import Datetime, Numeric, Text

from .airbyte_message_with_cached_json import AirbyteMessageWithCachedJSON
from .utils import format_airbyte_time, now_millis

"""The Wide Column Generator is not meant to mimic any datasets in particular, but is purely for stress testing
Users configure their desired number of columns and this will generate a row with random values matching the given schema.
This is tightly coupled to wide_column_schema_generator.py which defines the schema 
"""
class WideColumnGenerator:
    def __init__(self, stream_name: str, seed: int, record_keys: List[str], generate_errors_in_wide_columns: int) -> None:
        self.stream_name = stream_name
        self.seed = seed
        self.record_keys = record_keys
        self.generate_errors_in_wide_columns = generate_errors_in_wide_columns
        self.generated_errors = 0

    def increment_error_count(self):
        with Lock():
            self.generated_errors += 1

    def new_record(self) -> Mapping[str, Any]:
        def next_value(of_type: str):
            # switch statements in 3.10 :(
            if of_type == "string":
                return text.word()
            elif of_type == "boolean":
                return choice([True, False])
            elif of_type == "date":
                return dt.formatted_date(fmt="%Y-%m-%d")
            elif of_type == "timestamp_wo_tz":
                return dt.formatted_datetime(fmt="%Y-%m-%dT%H:%M:%S.%f")
            elif of_type == "timestamp_w_tz":
                # for whatever reason random timezones aren't working
                return dt.formatted_datetime(fmt="%Y-%m-%dT%H:%M:%S.%f-08:00")
            elif of_type == "time_wo_tz":
                return dt.formatted_time(fmt="%H:%M:%S.%f")
            elif of_type == "time_w_tz":
                # for whatever reason random timezones aren't working
                return dt.formatted_time(fmt="%H:%M:%S.%f-08:00")
            elif of_type == "integer":
                if self.generated_errors < self.generate_errors_in_wide_columns:
                    self.increment_error_count()
                    return text.word()
                return numeric.integer_number()
            elif of_type == "number":
                return numeric.decimal_number()
            elif of_type == "array":
                return [text.word() for _ in range(3)]
            elif of_type == "object":
                return {text.word(): text.word() for _ in range(3)}
            elif of_type == "union":
                return choice([lambda: text.word(), lambda: numeric.decimal_number()])()

        record = dict()
        for key in self.record_keys:
            if key == "id":
                record["id"] = numeric.increment()
            elif key == "updated_at":
                record["updated_at"] = format_airbyte_time(datetime.datetime.now())
            else:
                last_underscore = key.rfind("_")
                if last_underscore > 0:
                    record[key] = next_value(key[:last_underscore])
        return record

    def prepare(self):
        """
        Note: the instances of the mimesis generators need to be global.
        Yes, they *should* be able to be instance variables on this class, which should only instantiated once-per-worker, but that's not quite the case:
        * relying only on prepare as a pool initializer fails because we are calling the parent process's method, not the fork
        * Calling prepare() as part of generate() (perhaps checking if self.person is set) and then `print(self, current_process()._identity, current_process().pid)` reveals multiple object IDs in the same process, resetting the internal random counters
        """

        seed_with_offset = self.seed
        if self.seed is not None and len(current_process()._identity) > 0:
            seed_with_offset = self.seed + current_process()._identity[0]

        global dt
        global numeric
        global text

        dt = Datetime(seed=seed_with_offset)
        numeric = Numeric(seed=seed_with_offset)
        text = Text(seed=seed_with_offset)

    def generate(self, user_id: int) -> List[Dict]:
        row = self.new_record()
        record = AirbyteRecordMessage(stream=self.stream_name, data=row, emitted_at=now_millis())
        return AirbyteMessageWithCachedJSON(type=Type.RECORD, record=record)
