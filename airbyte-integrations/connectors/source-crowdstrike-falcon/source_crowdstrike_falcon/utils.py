#
# Copyright (c) 2023 Onyxia, Inc., all rights reserved.
#
import logging
from typing import Dict
from requests.auth import AuthBase
from .authenticator import CrowdstrikeFalconOauth2Authenticator

logger = logging.getLogger("airbyte")

def initialize_authenticator(config: Dict) -> AuthBase:
    logger.info(config)
    return CrowdstrikeFalconOauth2Authenticator(
        base_url=config.get("base_url"),
        client_secret=config.get("client_secret"),
        client_id=config.get("client_id"),
    )
