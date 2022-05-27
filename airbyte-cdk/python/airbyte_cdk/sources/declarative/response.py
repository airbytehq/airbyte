#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass
class Response:
    body: Optional[Mapping[str, Any]] = None
    headers: Optional[Mapping[str, Any]] = None
