# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

import dagger
import sys

DAGGER_EXEC_TIMEOUT =  dagger.Timeout(60 * 60) # One hour
DAGGER_CONFIG = dagger.Config(timeout=DAGGER_EXEC_TIMEOUT, log_output=sys.stderr)
