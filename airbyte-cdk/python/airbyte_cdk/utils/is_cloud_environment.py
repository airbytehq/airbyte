#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os

CLOUD_DEPLOYMENT_MODE = "cloud"


def is_cloud_environment() -> bool:
    """
    Returns True if the connector is running in a cloud environment, False otherwise.

    The function checks the value of the DEPLOYMENT_MODE environment variable which is set by the platform.
    This function can be used to determine whether stricter security measures should be applied.
    """
    deployment_mode = os.environ.get("DEPLOYMENT_MODE", "")
    return deployment_mode.casefold() == CLOUD_DEPLOYMENT_MODE
