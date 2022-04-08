#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

# Initialize Streams Package
from .core import Stream, IncrementalMixin

__all__ = ["Stream", "IncrementalMixin"]
