# Copyright (c) 2026 Airbyte, Inc., all rights reserved.

import os


pytest_plugins = ["airbyte_cdk.test.utils.manifest_only_fixtures"]

os.environ.setdefault("REQUEST_CACHE_PATH", "REQUEST_CACHE_PATH")
