#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from typing import List

from ci_connector_ops import utils

RELEASE_STAGES_TO_CHECK = ["generally_available", "beta"]


def get_connectors_missing_allowed_hosts() -> List[utils.Connector]:
    connectors_missing_allowed_hosts: List[utils.Connector] = []
    changed_connectors = utils.get_changed_connectors(destination=False, third_party=False)

    for connector in changed_connectors:
        if connector.release_stage in RELEASE_STAGES_TO_CHECK:
            missing = not connector_has_allowed_hosts(connector)
            if missing:
                connectors_missing_allowed_hosts.append(connector)

    return connectors_missing_allowed_hosts


def connector_has_allowed_hosts(connector: utils.Connector) -> bool:
    return connector.allowed_hosts is not None


def check_allowed_hosts():
    connectors_missing_allowed_hosts = get_connectors_missing_allowed_hosts()
    if connectors_missing_allowed_hosts:
        logging.error(f"The following {RELEASE_STAGES_TO_CHECK} connectors must include allowedHosts: {connectors_missing_allowed_hosts}")
        sys.exit(1)
    else:
        sys.exit(0)
