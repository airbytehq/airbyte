#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Iterable, List, Mapping

import requests

from airbyte_cdk.models import SyncMode
from source_amazon_ads.streams.common import AmazonAdsStream


class Profiles(AmazonAdsStream):
    """
    This stream corresponds to Amazon Advertising API - Profiles
    https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#/Profiles
    """

    is_resumable = False
    primary_key = "profileId"

    def path(self, **kwargs) -> str:
        return "v2/profiles?profileTypeFilter=seller,vendor"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            # Populate self._profiles list with profiles objects to not make
            # unnecessary API calls.
            self._profiles.append(record)
            yield record

    def read_records(self, *args, **kwargs) -> Iterable[Mapping[str, Any]]:
        if self._profiles:
            # In case if we have _profiles populated we can use it instead of making API call.
            yield from [profile for profile in self._profiles]
        else:
            # Make API call by the means of basic HttpStream class.
            yield from super().read_records(*args, **kwargs)

    def get_all_profiles(self) -> List[dict[str, Any]]:
        """
        Fetch all profiles and return it as list. We need this to set
        dependecies for other streams since all of the Amazon Ads API calls
        require profile id to be passed.
        :return List of profile object
        """
        return [profile for profile in self.read_records(SyncMode.full_refresh)]
