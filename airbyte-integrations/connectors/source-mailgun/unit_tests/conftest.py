# Copyright (c) 2025 Airbyte, Inc., all rights reserved.

import os


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")
