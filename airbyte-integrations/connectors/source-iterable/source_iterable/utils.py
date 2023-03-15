#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Mapping

import dateutil.parser
import pendulum
import requests


def dateutil_parse(text):
    """
    The custom function `dateutil_parse` replace `pendulum.parse(text, strict=False)` to avoid memory leak.
    More details https://github.com/airbytehq/airbyte/pull/19913
    """
    dt = dateutil.parser.parse(text)
    return pendulum.datetime(
        dt.year,
        dt.month,
        dt.day,
        dt.hour,
        dt.minute,
        dt.second,
        dt.microsecond,
        tz=dt.tzinfo or pendulum.tz.UTC,
    )


class IterableGenericErrorHandler:

    logger = logging.getLogger("airbyte")

    error_count = 0
    max_retry = 2

    def handle(self, response: requests.Response, stream_name: str, last_slice: Mapping[str, Any] = {}) -> bool:
        # error pattern to check
        code_pattern = "Generic Error"
        msg_pattern = "Please try again later"
        # prepare warning message
        warning_msg = f"Generic Server Error occured for stream: `{stream_name}`. "
        # For cases when there is a slice to go with, but server returns Generic Error - Please try again
        # we reetry 2 times, then skipp the record and move on with warning message.
        if response.json().get("code") == code_pattern and msg_pattern in response.json().get("msg"):
            self.error_count += 1
            setattr(self, "raise_on_http_errors", False)
            if self.error_count > self.max_retry:
                self.logger.warn(warning_msg + f"Skip fetching for slice {last_slice}.")
                return False
            else:
                self.logger.warn(warning_msg + f"Retrying for slice {last_slice}, attempt {self.error_count}")
                return True
        else:
            # All other cases
            return True
