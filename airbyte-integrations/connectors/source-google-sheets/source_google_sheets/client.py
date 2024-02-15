#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Dict, List, Mapping, Any

import backoff
from googleapiclient import errors
from requests import codes as status_codes

from .helpers import SCOPES, Helpers

logger = logging.getLogger("airbyte")


class GoogleSheetsClient:
    class Backoff:

        @staticmethod
        def give_up(error):
            code = error.resp.status
            # Stop retrying if it's not a problem with the rate limit or on the server end
            return not (code == status_codes.TOO_MANY_REQUESTS or 500 <= code < 600)

    def __init__(self, credentials: Dict[str, str], scopes: List[str] = SCOPES):
        self.client = Helpers.get_authenticated_sheets_client(credentials, scopes)
    
    def get_batch_size(self, config: Mapping[int, Any]):
        return config.get('batch_size')

    def _create_range(self, sheet, row_cursor, row_batch_size):
        range = f"{sheet}!{row_cursor}:{row_cursor + row_batch_size}"
        return range

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=Backoff.give_up)
    def get(self, **kwargs):
        return self.client.get(**kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=Backoff.give_up)
    def create(self, **kwargs):
        return self.client.create(**kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=Backoff.give_up)
    def get_values(self, **kwargs):
        range = self._create_range(kwargs.pop("sheet"), kwargs.pop("row_cursor"), kwargs.pop("row_batch_size"))
        logger.info(f"Fetching range {range}")
        return self.client.values().batchGet(ranges=range, **kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=Backoff.give_up)
    def update_values(self, **kwargs):
        return self.client.values().batchUpdate(**kwargs).execute()
