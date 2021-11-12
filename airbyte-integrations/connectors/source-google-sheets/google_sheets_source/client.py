#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


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

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=error_handler)
    def get(self, **kwargs):
        return self.client.get(**kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=error_handler)
    def create(self, **kwargs):
        return self.client.create(**kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=error_handler)
    def get_values(self, **kwargs):
        return self.client.values().batchGet(**kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=error_handler)
    def update_values(self, **kwargs):
        return self.client.values().batchUpdate(**kwargs).execute()
