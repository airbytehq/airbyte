#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from importlib import metadata

from .connector import AirbyteSpec, Connector
from .entrypoint import AirbyteEntrypoint
from .logger import AirbyteLogger

__all__ = ["AirbyteEntrypoint", "AirbyteLogger", "AirbyteSpec", "Connector"]
__version__ = metadata.version("airbyte_cdk")
