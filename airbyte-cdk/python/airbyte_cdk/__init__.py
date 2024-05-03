#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from .connector import Connector
from .entrypoint import AirbyteEntrypoint
from importlib import metadata

__all__ = ["AirbyteEntrypoint", "Connector"]
__version__ = metadata.version("airbyte_cdk")
