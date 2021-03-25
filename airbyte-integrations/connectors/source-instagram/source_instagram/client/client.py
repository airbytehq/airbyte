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

from typing import Any, List, Mapping, Tuple

import backoff
import pendulum
from base_python import BaseClient
from base_python.entrypoint import logger
from cached_property import cached_property
from facebook_business import FacebookAdsApi
from facebook_business.adobjects import user as fb_user
from facebook_business.adobjects.iguser import IGUser
from facebook_business.adobjects.page import Page
from facebook_business.api import Cursor
from facebook_business.exceptions import FacebookRequestError

from .api import MediaAPI, MediaInsightsAPI, StoriesAPI, StoriesInsightsAPI, UserInsightsAPI, UserLifetimeInsightsAPI, UsersAPI
from .common import InstagramAPIException, retry_pattern

backoff_policy = retry_pattern(backoff.expo, FacebookRequestError, max_tries=5, factor=5)


class Client(BaseClient):
    def __init__(self, access_token: str, start_date: str):
        self._start_date = pendulum.parse(start_date)

        self._api = FacebookAdsApi.init(access_token=access_token)
        self._apis = {
            "media": MediaAPI(self),
            "media_insights": MediaInsightsAPI(self),
            "stories": StoriesAPI(self),
            "story_insights": StoriesInsightsAPI(self),
            "users": UsersAPI(self),
            "user_lifetime_insights": UserLifetimeInsightsAPI(self),
            "user_insights": UserInsightsAPI(self),
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
    def accounts(self):
        return self._find_accounts()

    def _find_accounts(self) -> List:
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

    def health_check(self) -> Tuple[bool, str]:
        alive = True
        error_message = None
        try:
            self._find_accounts()
        except InstagramAPIException as exc:
            logger.error(str(exc))
            alive = False
            error_message = str(exc)

        return alive, error_message
