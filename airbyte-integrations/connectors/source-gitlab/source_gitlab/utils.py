#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Tuple


def parse_url(url: str) -> Tuple[bool, str, str]:
    parts = url.split("://")
    if len(parts) > 1:
        scheme, url = parts
    else:
        scheme = "https"
    if scheme not in ("http", "https"):
        return False, "", ""
    parts = url.split("/", 1)
    if len(parts) > 1:
        return False, "", ""
    host, *_ = parts
    return True, scheme, host
