# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import Path, RecordBuilder, find_template


class MondayRecordBuilder(RecordBuilder):
    @staticmethod
    def extract_record(resource: str, execution_folder: str, data_field: Path):
        return data_field.extract(find_template(resource=resource, execution_folder=execution_folder))
