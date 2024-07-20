import logging
from typing import Optional

from destination_palantir_foundry.config.foundry_config import FoundryConfig
from destination_palantir_foundry.foundry_api.foundry_auth import ConfidentialClientAuthFactory
from destination_palantir_foundry.foundry_api.service_factory import FoundryServiceFactory

FAILED_TO_AUTHENTICATE = "Failed to authenticate with Foundry. Please check your host name and credentials."
PROJECT_DOESNT_EXIST = "Project doesn't exist or the user doesn't have access to it."

CONFIG_VALIDATION_SCOPES = ["api:datasets-read"]


class ConfigValidator:
    def __init__(self, logger: logging.Logger, confidential_client_auth_factory: ConfidentialClientAuthFactory) -> None:
        self.logger = logger
        self.confidential_client_auth_factory = confidential_client_auth_factory

    def get_config_errors(self, config: FoundryConfig) -> Optional[str]:
        self.logger.info("Validating client credentials.")
        try:
            auth = self.confidential_client_auth_factory.create(
                config, CONFIG_VALIDATION_SCOPES)

            auth.sign_in_as_service_user()
        except Exception as e:
            # TODO(jcrowson): Actually match exception types
            self.logger.warn(
                f"Failed to authenticate with Foundry at host {config.host}. Error: {e}")
            return FAILED_TO_AUTHENTICATE

        service_factory = FoundryServiceFactory(config.host, auth)
        compass = service_factory.compass()
        try:
            compass.get_resource(config.destination_config.project_rid)
        except Exception as e:
            self.logger.warn(
                f"Project with rid {config.destination_config.project_rid} doesn't exist or the user doesn't have access to it. Error: {e}")
            return PROJECT_DOESNT_EXIST

        return None
