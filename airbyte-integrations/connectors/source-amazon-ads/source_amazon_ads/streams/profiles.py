#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from typing import Any, Iterable, List, Mapping

import requests
from airbyte_cdk.models import SyncMode
from source_amazon_ads.schemas import Profile
from source_amazon_ads.streams.common import AmazonAdsStream


class Profiles(AmazonAdsStream):
    """
    This stream corresponds to Amazon Advertising API - Profiles
    https://advertising.amazon.com/API/docs/en-us/reference/2/profiles#/Profiles
    """

    primary_key = "profileId"
    model = Profile

    def path(self, **kvargs) -> str:
        return "v2/profiles"

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        for record in super().parse_response(response, **kwargs):
            profile_id_obj = self.model.parse_obj(record)
            # Populate self._profiles list with profiles objects to not make
            # unnecessary API calls.
            self._profiles.append(profile_id_obj)
            yield record

    def read_records(self, *args, **kvargs) -> Iterable[Mapping[str, Any]]:
        if self._profiles:
            # In case if we have _profiles populated we can use it instead of making API call.
            yield from [profile.dict(exclude_unset=True) for profile in self._profiles]
        else:
            # Make API call by the means of basic HttpStream class.
            yield from super().read_records(*args, **kvargs)

    def get_all_profiles(self) -> List[Profile]:
        """
        Fetch all profiles and return it as list. We need this to set
        dependecies for other streams since all of the Amazon Ads API calls
        require profile id to be passed.
        :return List of profile object
        """
        return [self.model.parse_obj(profile) for profile in self.read_records(SyncMode.full_refresh)]
