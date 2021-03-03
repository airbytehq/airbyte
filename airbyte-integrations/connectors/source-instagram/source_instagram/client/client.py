"""
MIT License

Copyright (c) 2020 Airbyte

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, Mapping, Tuple

import pendulum
from base_python import BaseClient
from base_python.entrypoint import logger
from cached_property import cached_property
from facebook_business import FacebookAdsApi
from facebook_business.adobjects import user as fb_user
from facebook_business.adobjects.iguser import IGUser
from facebook_business.adobjects.page import Page
from facebook_business.exceptions import FacebookRequestError

from .api import (
    IgMediaAPI,
    IgMediaInsightsAPI,
    IgStoriesAPI,
    IgStoriesInsightsAPI,
    IgUserInsightsAPI,
    IgUserLifetimeInsightsAPI,
    IgUsersAPI,
)


class Client(BaseClient):
    def __init__(self, account_id: str, access_token: str, start_date: str):
        self._account_id = account_id
        self._start_date = pendulum.parse(start_date)

        self._api = FacebookAdsApi.init(access_token=access_token)
        self._apis = {
            "media": IgMediaAPI(self),
            "stories": IgStoriesAPI(self),
            "users": IgUsersAPI(self),
            "user_lifetime_insights": IgUserLifetimeInsightsAPI(self),
            "user_insights": IgUserInsightsAPI(self),
            "media_insights": IgMediaInsightsAPI(self),
            "story_insights": IgStoriesInsightsAPI(self),
        }
        super().__init__()

    def _enumerate_methods(self) -> Mapping[str, callable]:
        """Detect available streams and return mapping"""
        return {name: api.list for name, api in self._apis.items()}

    def stream_has_state(self, name: str) -> bool:
        """Tell if stream supports incremental sync"""
        return hasattr(self._apis[name], "state")

    def get_stream_state(self, name: str) -> Any:
        """Get state of stream with corresponding name"""
        return self._apis[name].state

    def set_stream_state(self, name: str, state: Any):
        """Set state of stream with corresponding name"""
        self._apis[name].state = state

    @cached_property
    def account(self):
        return self._find_account(self._account_id)

    @staticmethod
    def _find_account(account_id: str):
        try:
            accounts = fb_user.User(fbid="me").get_accounts()
            for account in accounts:
                page = Page(account.get_id()).api_get(fields=["instagram_business_account"])
                if page.get("instagram_business_account") and page.get("instagram_business_account").get("id") == account_id:
                    return IGUser(page.get("instagram_business_account").get("id"))
        except FacebookRequestError as exc:
            raise Exception(f"Error: {exc.api_error_code()}, {exc.api_error_message()}") from exc

        raise Exception(f"Couldn't find Instagram business account with id {account_id}")

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_message = None
        try:
            self._find_account(self._account_id)
        except Exception as exc:
            logger.error(str(exc))
            alive = False
            error_message = str(exc)

        return alive, error_message
