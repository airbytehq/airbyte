#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Union, Any, Mapping
from airbyte_cdk.models import AirbyteMessage, AirbyteStream, SyncMode

JsonType = Union[dict[str, "JsonType"], list["JsonType"], str, int, float, bool, None]
StreamData = Union[Mapping[str, Any], AirbyteMessage]
