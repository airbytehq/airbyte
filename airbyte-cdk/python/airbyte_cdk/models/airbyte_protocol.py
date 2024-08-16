#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from airbyte_protocol_dataclasses.models import *


from dataclasses import dataclass, InitVar
from typing import Mapping



@dataclass
class AirbyteStateBlob:
    kwargs: InitVar[Mapping[str, Any]]

    def __post_init__(self, kwargs):
        self.__dict__.update(kwargs)


from airbyte_protocol.models import ConfiguredAirbyteCatalog