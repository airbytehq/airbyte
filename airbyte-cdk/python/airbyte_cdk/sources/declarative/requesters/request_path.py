#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from collections.abc import Mapping
from dataclasses import InitVar, dataclass
from typing import Any


@dataclass
class RequestPath:
    """Describes that a component value should be inserted into the path"""

    parameters: InitVar[Mapping[str, Any]]
