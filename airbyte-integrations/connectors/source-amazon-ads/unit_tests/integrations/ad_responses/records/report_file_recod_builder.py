# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, RecordBuilder, find_template


class ReportFileRecordBuilder(RecordBuilder):
    @classmethod
    def report_file_record(cls):
        return cls(find_template("download_report_file", __file__)[0], FieldPath("campaignId"), None)
