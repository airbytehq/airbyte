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

from typing import Dict, List

import backoff
from googleapiclient import errors
from requests import codes as status_codes

from .helpers import SCOPES, Helpers


def error_handler(error):
    return error.resp.status != status_codes.TOO_MANY_REQUESTS


class GoogleSheetsClient:
    def __init__(self, credentials: Dict[str, str], scopes: List[str] = SCOPES):
        self.client = Helpers.get_authenticated_sheets_client(credentials, scopes)

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=60, giveup=error_handler)
    def get(self, **kwargs):
        return self.client.get(**kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=60, giveup=error_handler)
    def create(self, **kwargs):
        return self.client.create(**kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=60, giveup=error_handler)
    def get_values(self, **kwargs):
        return self.client.values().batchGet(**kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=60, giveup=error_handler)
    def update_values(self, **kwargs):
        return self.client.values().batchUpdate(**kwargs).execute()
