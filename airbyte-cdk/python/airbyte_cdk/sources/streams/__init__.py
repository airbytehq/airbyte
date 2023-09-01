#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# Initialize Streams Package
from .core import IncrementalMixin, Stream

__all__ = ["IncrementalMixin", "Stream"]
