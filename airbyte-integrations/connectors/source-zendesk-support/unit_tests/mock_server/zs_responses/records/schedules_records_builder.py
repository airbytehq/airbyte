# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class SchedulesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def schedules_record(cls) -> "SchedulesRecordBuilder":
        record_template = cls.extract_record("schedules", __file__, NestedPath(["schedules", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "SchedulesRecordBuilder":
        self._record["id"] = id
        return self
