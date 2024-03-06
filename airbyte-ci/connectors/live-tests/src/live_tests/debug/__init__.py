# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import dagger
import os
import sys

DAGGER_EXEC_TIMEOUT = dagger.Timeout(int(os.environ.get("DAGGER_EXEC_TIMEOUT", "3600")))  # One hour by default
DAGGER_CONFIG = dagger.Config(timeout=DAGGER_EXEC_TIMEOUT, log_output=sys.stderr)
