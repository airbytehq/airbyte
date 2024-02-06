# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, RecordBuilder, find_template


class ZendeskSupportRecordBuilder(RecordBuilder):
    @staticmethod
    def extract_record(resource: str, execution_folder: str, data_field: FieldPath):
        return data_field.extract(find_template(resource=resource, execution_folder=execution_folder))
