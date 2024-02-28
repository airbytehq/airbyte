#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
import pytest

@pytest.fixture
def setup_deployment_mode():
    os.environ["DEPLOYMENT_MODE"] = "testing"

    yield

    os.environ.pop("DEPLOYMENT_MODE", None)