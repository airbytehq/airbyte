#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from .source import SourceSalesforce
from .source_dynamic import SourceDynamicSalesforce

__all__ = ["SourceSalesforce", "SourceDynamicSalesforce"]
