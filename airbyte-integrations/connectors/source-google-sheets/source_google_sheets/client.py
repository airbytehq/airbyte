#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Dict, List

import backoff
from googleapiclient import errors
from requests import codes as status_codes

from .helpers import SCOPES, Helpers


logger = logging.getLogger("airbyte")


class GoogleSheetsClient:
    class Backoff:
        row_batch_size = 200

        @classmethod
        def increase_row_batch_size(cls, details):
            if details["exception"].status_code == status_codes.TOO_MANY_REQUESTS and cls.row_batch_size < 1000:
                cls.row_batch_size = cls.row_batch_size + 100
                logger.info(f"Increasing number of records fetching due to rate limits. Current value: {cls.row_batch_size}")

        @staticmethod
        def give_up(error):
            code = error.resp.status
            # Stop retrying if it's not a problem with the rate limit or on the server end
            return not (code == status_codes.TOO_MANY_REQUESTS or 500 <= code < 600)

    def __init__(self, credentials: Dict[str, str], scopes: List[str] = SCOPES):
        self.client = Helpers.get_authenticated_sheets_client(credentials, scopes)

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=Backoff.give_up, on_backoff=Backoff.increase_row_batch_size)
    def get(self, **kwargs):
        return self.client.get(**kwargs).execute()

    @backoff.on_exception(backoff.expo, errors.HttpError, max_time=120, giveup=Backoff.give_up, on_backoff=Backoff.increase_row_batch_size)
    def get_values(self, **kwargs):
        range = self._create_range(kwargs.pop("sheet"), kwargs.pop("row_cursor"))
        logger.info(f"Fetching range {range}")
        return self.client.values().batchGet(ranges=range, **kwargs).execute()

    def _create_range(self, sheet, row_cursor):
        range = f"{sheet}!{row_cursor}:{row_cursor + self.Backoff.row_batch_size}"
        return range
