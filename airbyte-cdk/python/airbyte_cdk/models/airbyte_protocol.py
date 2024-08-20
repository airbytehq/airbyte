#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import serpyco_rs
from airbyte_protocol_dataclasses.models import *


from dataclasses import dataclass, InitVar
from typing import Mapping



@dataclass
class AirbyteStateBlob:
    kwargs: InitVar[Mapping[str, Any]]

    # def __post_init__(self, kwargs):
    #     self.__dict__.update(kwargs)
    def __init__(self, *args, **kwargs):
        # Set any attribute passed in through kwargs
        for arg in args:
            self.__dict__.update(arg)
        for key, value in kwargs.items():
            setattr(self, key, value)

from airbyte_protocol.models import ConfiguredAirbyteCatalog

AirbyteMessageSerializer = serpyco_rs.Serializer(AirbyteMessage, omit_none=True)