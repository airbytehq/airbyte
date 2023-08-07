#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import random

from connector_ops.utils import Connector, ConnectorLanguage, get_all_connectors_in_repo

ALL_CONNECTORS = get_all_connectors_in_repo()


def pick_a_random_connector(
    language: ConnectorLanguage = None, release_stage: str = None, other_picked_connectors: list = None
) -> Connector:
    """Pick a random connector from the list of all connectors."""
    all_connectors = list(ALL_CONNECTORS)
    if language:
        all_connectors = [c for c in all_connectors if c.language is language]
    if release_stage:
        all_connectors = [c for c in all_connectors if c.release_stage == release_stage]
    picked_connector = random.choice(all_connectors)
    if other_picked_connectors:
        while picked_connector in other_picked_connectors:
            picked_connector = random.choice(all_connectors)
    return picked_connector
