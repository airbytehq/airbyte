#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from typing import List

from connector_ops import utils


def get_connectors_missing_allowed_hosts() -> List[utils.Connector]:
    connectors_missing_allowed_hosts: List[utils.Connector] = []
    changed_connectors = utils.get_changed_connectors(destination=False, third_party=False)

    for connector in changed_connectors:
        if connector.requires_allowed_hosts_check:
            missing = not connector_has_allowed_hosts(connector)
            if missing:
                connectors_missing_allowed_hosts.append(connector)

    return connectors_missing_allowed_hosts


def connector_has_allowed_hosts(connector: utils.Connector) -> bool:
    return connector.allowed_hosts is not None


def check_allowed_hosts():
    connectors_missing_allowed_hosts = get_connectors_missing_allowed_hosts()
    if connectors_missing_allowed_hosts:
        logging.error(f"The following connectors must include allowedHosts: {connectors_missing_allowed_hosts}")
        sys.exit(1)
    else:
        sys.exit(0)
