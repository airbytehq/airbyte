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

from typing import List, Tuple, Mapping, Any

import backoff
from cached_property import cached_property
from facebook_business import FacebookAdsApi
from facebook_business.adobjects import user as fb_user
from facebook_business.adobjects.iguser import IGUser
from facebook_business.adobjects.page import Page
from facebook_business.api import Cursor
from facebook_business.exceptions import FacebookRequestError

from source_instagram.common import InstagramAPIException, retry_pattern

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=4, factor=5)


class InstagramAPI:
    def __init__(self, access_token: str):
        self._api = FacebookAdsApi.init(access_token=access_token)

    @cached_property
    def accounts(self) -> List[Mapping[str, Any]]:
        return self._find_accounts()

    @cached_property
    def user(self) -> IGUser:
        return self._get_instagram_user()

    def _find_accounts(self) -> List[Mapping[str, Any]]:
        try:
            instagram_business_accounts = []
            accounts = self._get_accounts()
            for account in accounts:
                page = Page(account.get_id()).api_get(fields=["instagram_business_account"])
                if page.get("instagram_business_account"):
                    instagram_business_accounts.append(
                        {
                            "page_id": account.get_id(),
                            "instagram_business_account": self._get_instagram_user(page),
                        }
                    )
        except FacebookRequestError as exc:
            raise InstagramAPIException(f"Error: {exc.api_error_code()}, {exc.api_error_message()}") from exc

        if instagram_business_accounts:
            return instagram_business_accounts
        raise InstagramAPIException("Couldn't find an Instagram business account for current Access Token")

    @backoff_policy
    def _get_accounts(self) -> Cursor:
        return fb_user.User(fbid="me").get_accounts()

    @backoff_policy
    def _get_instagram_user(self, page: Page) -> IGUser:
        return IGUser(page.get("instagram_business_account").get("id"))
