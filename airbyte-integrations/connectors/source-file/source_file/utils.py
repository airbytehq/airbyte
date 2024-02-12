#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from urllib.parse import parse_qs, urlencode, urlparse

# default logger
logger = logging.getLogger("airbyte")

LOCAL_STORAGE_NAME = "local"


def dropbox_force_download(url):
    """
    https://help.dropbox.com/share/force-download
    """
    parse_result = urlparse(url)
    if parse_result.netloc.split(".")[-2:] == ["dropbox", "com"]:
        qs = parse_qs(parse_result.query)
        if qs.get("dl") == ["0"]:
            qs["dl"] = "1"
            parse_result = parse_result._replace(query=urlencode(qs))
    return parse_result.geturl()


def backoff_handler(details):
    logger.info(f"Caught retryable error after {details['tries']} tries. Waiting {details['wait']} seconds then retrying...")
