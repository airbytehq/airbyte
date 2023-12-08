#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Any

StreamSlice = Mapping[str, Any]
StreamState = MutableMapping[str, Any]
