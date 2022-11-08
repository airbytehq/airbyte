#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass


@dataclass
class Response:
    body: dict
    headers: dict
    status_code: int
