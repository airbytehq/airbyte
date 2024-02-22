#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os


def pytest_configure(config):
    os.environ["DEPLOYMENT_MODE"] = "testing"

def pytest_unconfigure(config):
    os.environ.pop("DEPLOYMENT_MODE", None)