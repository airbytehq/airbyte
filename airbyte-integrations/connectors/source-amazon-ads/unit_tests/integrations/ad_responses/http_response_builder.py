# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from airbyte_cdk.test.mock_http.response_builder import HttpResponseBuilder


class AmazonAdsHttpResponseBuilder(HttpResponseBuilder):
    def with_pagination(self) -> "AmazonAdsHttpResponseBuilder":
        if not self._pagination_strategy:
            super().with_pagination()
        else:
            self._pagination_strategy.update(self._records)
            return self
