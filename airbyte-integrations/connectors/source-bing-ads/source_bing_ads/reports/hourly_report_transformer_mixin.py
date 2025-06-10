#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer
from source_bing_ads.utils import transform_report_hourly_datetime_format_to_rfc_3339


class HourlyReportTransformerMixin:
    transformer: TypeTransformer = TypeTransformer(TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization)

    @staticmethod
    @transformer.registerCustomTransform
    def custom_transform_datetime_rfc3339(original_value, field_schema):
        if original_value and "format" in field_schema and field_schema["format"] == "date-time":
            transformed_value = transform_report_hourly_datetime_format_to_rfc_3339(original_value)
            return transformed_value
        return original_value
