from typing import Dict, Any

import pendulum

from airbyte_cdk.sources.utils.transform import TypeTransformer, TransformConfig



class LedgerDetailedViewReportsTypeTransformer(TypeTransformer):

    def __init__(self, *args, **kwargs):
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: str, field_schema: Dict[str, Any]) -> str:
            if original_value and field_schema.get("format") == "date":
                date_format = "MM/YYYY" if len(original_value) <= 7 else "MM/DD/YYYY"
                try:
                    transformed_value = pendulum.from_format(original_value, date_format).to_date_string()
                    return transformed_value
                except ValueError:
                    pass
            return original_value

        return transform_function