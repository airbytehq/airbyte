# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class BrandsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def brands_record(cls) -> "BrandsRecordBuilder":
        record_template = cls.extract_record("brands", __file__, NestedPath(["brands", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))

    def with_id(self, id: int) -> "BrandsRecordBuilder":
        self._record["id"] = id
        return self
