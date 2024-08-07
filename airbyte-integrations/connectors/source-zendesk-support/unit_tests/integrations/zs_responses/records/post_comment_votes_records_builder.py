# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, NestedPath

from .records_builder import ZendeskSupportRecordBuilder


class PostCommentVotesRecordBuilder(ZendeskSupportRecordBuilder):
    @classmethod
    def post_commetn_votes_record(cls) -> "PostCommentVotesRecordBuilder":
        record_template = cls.extract_record("votes", __file__, NestedPath(["votes", 0]))
        return cls(record_template, FieldPath("id"), FieldPath("updated_at"))
