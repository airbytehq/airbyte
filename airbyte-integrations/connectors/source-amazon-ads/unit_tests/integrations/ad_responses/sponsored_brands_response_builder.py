# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from typing import Optional

from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder, PaginationStrategy, RootPath, find_template


class SponsoredBrandsResponseBuilder(HttpResponseBuilder):
    @classmethod
    def ad_groups_response(cls, pagination_strategy: Optional[PaginationStrategy] = None) -> "SponsoredBrandsResponseBuilder":
        return cls(find_template("sponsored_brands_ad_groups", __file__), RootPath(), pagination_strategy)

    @classmethod
    def ad_groups_non_breaking_error_response(
        cls, pagination_strategy: Optional[PaginationStrategy] = None
    ) -> "SponsoredBrandsResponseBuilder":
        return cls(find_template("non_breaking_error", __file__), RootPath(), pagination_strategy)

    @classmethod
    def campaigns_response(cls, pagination_strategy: Optional[PaginationStrategy] = None) -> "SponsoredBrandsResponseBuilder":
        return cls(find_template("sponsored_brands_campaigns", __file__), RootPath(), pagination_strategy)

    @classmethod
    def keywords_response(cls, pagination_strategy: Optional[PaginationStrategy] = None) -> "SponsoredBrandsResponseBuilder":
        return cls(find_template("sponsored_brands_keywords", __file__), RootPath(), pagination_strategy)

    def with_pagination(self) -> "SponsoredBrandsResponseBuilder":
        if not self._pagination_strategy:
            super().with_pagination()
        else:
            self._pagination_strategy.update(self._records)
            return self
