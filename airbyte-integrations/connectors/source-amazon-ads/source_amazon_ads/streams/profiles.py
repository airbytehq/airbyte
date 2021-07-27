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

from typing import Any, Iterable, Mapping

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
            self._ctx.profiles.append(profile_id_obj)
            yield record

    def read_records(self, *args, **kvargs) -> Iterable[Mapping[str, Any]]:
        if self._ctx.profiles:
            yield from [profile.dict(exclude_unset=True) for profile in self._ctx.profiles]
        else:
            yield from super().read_records(*args, **kvargs)

    def fill_context(self):
        """
        Fill profiles info for other streams in case of "profiles" stream havent been specified on catalog config
        """
        _ = [record for record in self.read_records(SyncMode.full_refresh)]
