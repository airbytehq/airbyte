# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class TicketFormsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def ticket_forms_record(cls) -> "TicketFormsRecordBuilder":
        record_template = cls.extract_record("ticket_forms", __file__, NestedPath(["ticket_forms", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))
