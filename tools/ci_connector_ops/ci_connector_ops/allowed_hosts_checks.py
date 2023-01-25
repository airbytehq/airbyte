#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import sys
from typing import List

from ci_connector_ops import utils

RELEASE_STAGES_TO_CHECK = ["generally_available", "beta"]

def get_connectors_missing_allowed_hosts() -> List[str]:
    connectors_missing_allowed_hosts = []
    changed_connector_names = utils.get_changed_connector_names()

    for connector_name in changed_connector_names:
        connector_release_stage = utils.get_connector_release_stage(connector_name)
        if connector_release_stage in RELEASE_STAGES_TO_CHECK:
          missing = not connector_has_allowed_hosts(connector_name)
          if missing:
            connectors_missing_allowed_hosts.append(connector_name)

    return connectors_missing_allowed_hosts

def connector_has_allowed_hosts(connector_name: str) -> bool:
  definition = utils.get_connector_definition(connector_name)
  # print("----- " + connector_name  + " -----")
  # print(definition)
    return definition.get("allowedHosts") is not None


def check_allowed_hosts():
    connectors_missing_allowed_hosts = get_connectors_missing_allowed_hosts()
    if connectors_missing_allowed_hosts:
        logging.error(
            f"The following {RELEASE_STAGES_TO_CHECK} connectors must include allowedHosts: {connectors_missing_allowed_hosts}"
        )
        sys.exit(1)
    else:
        sys.exit(0)



