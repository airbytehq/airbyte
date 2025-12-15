# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class AutomationsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def automations_record(cls) -> "AutomationsRecordBuilder":
        record_template = cls.extract_record("automations", __file__, NestedPath(["automations", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "AutomationsRecordBuilder":
        self._record["id"] = id
        return self
