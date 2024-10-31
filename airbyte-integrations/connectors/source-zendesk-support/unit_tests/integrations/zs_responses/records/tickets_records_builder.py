# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class TicketsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def tickets_record(cls) -> "TicketsRecordBuilder":
        record_template = cls.extract_record("tickets", __file__, NestedPath(["tickets", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("generated_timestamp"))
