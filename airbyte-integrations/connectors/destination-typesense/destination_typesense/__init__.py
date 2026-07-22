#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

# Apply CDK patches BEFORE importing anything else
# This fixes the "State message does not contain id" error with Airbyte 1.7+
from . import cdk_patches  # noqa: F401

from .destination import DestinationTypesense

__all__ = ["DestinationTypesense"]
