# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import FieldPath, RecordBuilder, find_template


class SponsoredBrandsRecordBuilder(RecordBuilder):
    @classmethod
    def ad_groups_record(cls) -> "SponsoredBrandsRecordBuilder":
        return cls(find_template("sponsored_brands_ad_groups", __file__)[0], FieldPath("adGroupId"), None)

    @classmethod
    def campaigns_record(cls) -> "SponsoredBrandsRecordBuilder":
        return cls(find_template("sponsored_brands_campaigns", __file__)[0], FieldPath("campaignId"), None)

    @classmethod
    def keywords_record(cls) -> "SponsoredBrandsRecordBuilder":
        return cls(find_template("sponsored_brands_keywords", __file__)[0], FieldPath("adGroupId"), None)
