#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from dataclasses import dataclass


@dataclass
class Request:
    url: str
    headers: dict
    body: dict
