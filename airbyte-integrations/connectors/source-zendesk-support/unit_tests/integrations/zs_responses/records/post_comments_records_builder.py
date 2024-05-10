# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class PostsCommentsRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def posts_commetns_record(cls) -> "PostsCommentsRecordBuilder":
        record_template = cls.extract_record("post_comments", __file__, NestedPath(["comments", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))
