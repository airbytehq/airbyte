#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from .test_core import TestBasicRead, TestConnection, TestDiscovery, TestSpec
from .test_full_refresh import TestFullRefresh
from .test_incremental import TestIncremental

__all__ = ["TestSpec", "TestBasicRead", "TestConnection", "TestDiscovery", "TestFullRefresh", "TestIncremental"]
