# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .record_builder import MondayRecordBuilder


class ItemsRecordBuilder(MondayRecordBuilder):
    @classmethod
    def items_record(cls) -> "ItemsRecordBuilder":
        record_template = cls.extract_record("items", __file__, NestedPath(["data", "boards", 0, "items_page", "items", 0]))
        return cls(record_template, FieldPath("id"), None)
