# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from typing import Any, Dict

import dateparser
import pendulum

from airbyte_cdk.sources.utils.transform import TransformConfig, TypeTransformer


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


class MerchantListingsFypReportTypeTransformer(TypeTransformer):
    def __init__(self, *args, **kwargs):
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date":
                try:
                    transformed_value = pendulum.from_format(original_value, "MMM D[,] YYYY").to_date_string()
                    return transformed_value
                except ValueError:
                    pass
            return original_value

        return transform_function


class MerchantReportsTypeTransformer(TypeTransformer):
    def __init__(self, *args, **kwargs):
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date-time":
                # open-date field is returned in format "2022-07-11 01:34:18 PDT"
                transformed_value = dateparser.parse(original_value).isoformat()
                return transformed_value
            return original_value

        return transform_function


class SellerFeedbackReportsTypeTransformer(TypeTransformer):
    config: Dict[str, Any] = None

    MARKETPLACE_DATE_FORMAT_MAP = dict(
        # eu
        A2VIGQ35RCS4UG="D/M/YY",  # AE
        A1PA6795UKMFR9="D.M.YY",  # DE
        A1C3SOZRARQ6R3="D/M/YY",  # PL
        ARBP9OOSHTCHU="D/M/YY",  # EG
        A1RKKUPIHCS9HS="D/M/YY",  # ES
        A13V1IB3VIYZZH="D/M/YY",  # FR
        A21TJRUUN4KGV="D/M/YY",  # IN
        APJ6JRA9NG5V4="D/M/YY",  # IT
        A1805IZSGTT6HS="D/M/YY",  # NL
        A17E79C6D8DWNP="D/M/YY",  # SA
        A2NODRKZP88ZB9="YYYY-MM-DD",  # SE
        A33AVAJ2PDY3EV="D/M/YY",  # TR
        A1F83G8C2ARO7P="D/M/YY",  # UK
        AMEN7PMS3EDWL="D/M/YY",  # BE
        # fe
        A39IBJ37TRP1C6="D/M/YY",  # AU
        A1VC38T7YXB528="YY/M/D",  # JP
        A19VAU5U5O7RUS="D/M/YY",  # SG
        # na
        ATVPDKIKX0DER="M/D/YY",  # US
        A2Q3Y263D00KWC="D/M/YY",  # BR
        A2EUQ1WTGCTBG2="D/M/YY",  # CA
        A1AM78C64UM0Y8="D/M/YY",  # MX
    )

    def __init__(self, *args, config, **kwargs):
        self.marketplace_id = config.get("marketplace_id")
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    def get_transform_function(self):
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value and field_schema.get("format") == "date":
                date_format = self.MARKETPLACE_DATE_FORMAT_MAP.get(self.marketplace_id)
                if not date_format:
                    raise KeyError(f"Date format not found for Marketplace ID: {self.marketplace_id}")
                try:
                    transformed_value = pendulum.from_format(original_value, date_format).to_date_string()
                    return transformed_value
                except ValueError:
                    pass

            return original_value

        return transform_function


class FlatFileSettlementV2ReportsTypeTransformer(TypeTransformer):
    def __init__(self, *args, **kwargs):
        config = TransformConfig.DefaultSchemaNormalization | TransformConfig.CustomSchemaNormalization
        super().__init__(config)
        self.registerCustomTransform(self.get_transform_function())

    @staticmethod
    def get_transform_function():
        def transform_function(original_value: Any, field_schema: Dict[str, Any]) -> Any:
            if original_value == "" and field_schema.get("format") == "date-time":
                return None
            return original_value

        return transform_function
