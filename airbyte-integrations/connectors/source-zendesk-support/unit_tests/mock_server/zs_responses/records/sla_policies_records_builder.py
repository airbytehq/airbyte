# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class SlaPoliciesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def sla_policies_record(cls) -> "SlaPoliciesRecordBuilder":
        record_template = cls.extract_record("sla_policies", __file__, NestedPath(["sla_policies", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "SlaPoliciesRecordBuilder":
        self._record["id"] = id
        return self

    def with_title(self, title: str) -> "SlaPoliciesRecordBuilder":
        self._record["title"] = title
        return self
