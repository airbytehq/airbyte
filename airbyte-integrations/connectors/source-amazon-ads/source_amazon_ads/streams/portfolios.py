#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, Mapping, MutableMapping

from source_amazon_ads.schemas import Portfolio
from source_amazon_ads.streams.common import AmazonAdsStream


class Portfolios(AmazonAdsStream):
    """
    This stream corresponds to Amazon Advertising API - Portfolios
    https://advertising.amazon.com/API/docs/en-us/reference/2/portfolios
    """

    primary_key = "portfolioId"
    model = Portfolio

    def path(self, **kvargs) -> str:
        return "v2/portfolios/extended"

    def read_records(self, *args, **kvargs) -> Iterable[Mapping[str, Any]]:
        """
        Iterate through self._profiles list and send read all records for each profile.
        """
        for profile in self._profiles:
            self._current_profile_id = profile.profileId
            yield from super().read_records(*args, **kvargs)

    def request_headers(self, *args, **kvargs) -> MutableMapping[str, Any]:
        headers = super().request_headers(*args, **kvargs)
        headers["Amazon-Advertising-API-Scope"] = str(self._current_profile_id)
        return headers
