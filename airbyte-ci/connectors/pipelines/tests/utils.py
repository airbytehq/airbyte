#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import random

from connector_ops.utils import Connector, ConnectorLanguage, get_all_connectors_in_repo

ALL_CONNECTORS = get_all_connectors_in_repo()


def pick_a_random_connector(
    language: ConnectorLanguage = None, support_level: str = None, other_picked_connectors: list = None
) -> Connector:
    """Pick a random connector from the list of all connectors."""
    # The Connector util is not good at fetching metadata for third party connectors.
    # We want to avoid picking a connector that does not have metadata.
    all_connectors = [c for c in list(ALL_CONNECTORS) if c.metadata is not None]
    if language:
        all_connectors = [c for c in all_connectors if c.language is language]
    if support_level:
        all_connectors = [c for c in all_connectors if c.support_level == support_level]
    picked_connector = random.choice(all_connectors)
    if other_picked_connectors:
        while picked_connector in other_picked_connectors:
            picked_connector = random.choice(all_connectors)
    return picked_connector
