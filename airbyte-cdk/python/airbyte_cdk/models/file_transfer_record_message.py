# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class AirbyteFileTransferRecordMessage:
    stream: str
    file: Dict[str, Any]
    emitted_at: int
    namespace: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
