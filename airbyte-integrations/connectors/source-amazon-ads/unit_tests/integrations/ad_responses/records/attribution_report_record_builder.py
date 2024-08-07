# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, RecordBuilder, find_template


class AttributionReportRecordBuilder(RecordBuilder):
    _field_path = FieldPath("reports")

    @classmethod
    def products_record(cls) -> "AttributionReportRecordBuilder":
        return cls(cls._field_path.extract(find_template("attribution_report_products", __file__))[0], None, None)

    @classmethod
    def performance_adgroup_record(cls) -> "AttributionReportRecordBuilder":
        return cls(cls._field_path.extract(find_template("attribution_report_performance_adgroup", __file__))[0], None, None)

    @classmethod
    def performance_campaign_record(cls) -> "AttributionReportRecordBuilder":
        return cls(cls._field_path.extract(find_template("attribution_report_performance_campaign", __file__))[0], None, None)

    @classmethod
    def performance_creative_record(cls) -> "AttributionReportRecordBuilder":
        return cls(cls._field_path.extract(find_template("attribution_report_performance_creative", __file__))[0], None, None)
