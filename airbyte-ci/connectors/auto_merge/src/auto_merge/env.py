# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from __future__ import annotations

import os

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
PRODUCTION = os.environ.get("AUTO_MERGE_PRODUCTION", "false").lower() == "true"
