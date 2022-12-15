#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging

LOGGER = logging.getLogger("airbyte")

HTTP_ERROR_CODES = {
    400: {
        "msg": "The file size of the exported data is too large. Shorten the time ranges and try again. The limit size is 4GB.",
        "lvl": "ERROR",
    },
    404: {
        "msg": "No data collected",
        "lvl": "WARN",
    },
    504: {
        "msg": "The amount of data is large causing a timeout. For large amounts of data, the Amazon S3 destination is recommended.",
        "lvl": "ERROR",
    },
}


def error_msg_from_status(status: int = None):
    if status:
        level = HTTP_ERROR_CODES[status]["lvl"]
        message = HTTP_ERROR_CODES[status]["msg"]
        if level == "ERROR":
            LOGGER.error(message)
        elif level == "WARN":
            LOGGER.warn(message)
        else:
            LOGGER.error(f"Unknown error occured: code {status}")
