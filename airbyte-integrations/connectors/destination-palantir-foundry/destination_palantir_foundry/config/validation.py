from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.compass import Compass
from foundry import ConfidentialClientAuth
from typing import Optional
import logging


def get_config_errors(logger: logging.Logger, config: FoundryConfig) -> Optional[str]:
    logger.info("Validating client credentials.")
    try:
        auth = ConfidentialClientAuth(
            client_id=config.auth.client_id,
            client_secret=config.auth.client_secret,
            hostname=config.host,
        )

        auth.sign_in_as_service_user()
    except Exception as e:
        logger.warn(f"Failed to authenticate with Foundry at host {config.host}", e)
        return "Failed to authenticate with Foundry. Please check your host name and credentials."
    
    compass = Compass(config, auth)
    try:
        compass.get_resource(config.destination_config.project_rid)
    except Exception as e:
        logger.warn(f"Project with rid {config.destination_config.project_rid} doesn't exist or the user doesn't have access to it.", e)
        return "Project doesn't exist or the user doesn't have access to it."
    
    return None
