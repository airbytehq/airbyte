#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, List, Mapping

from airbyte_cdk import emit_configuration_as_airbyte_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.message import InMemoryMessageRepository, MessageRepository


logger = logging.getLogger("airbyte_logger")


class MigrateCredentialsToOAuth:
    """Migrates flat credential fields into a nested `credentials` object.

    Before v2.8.0, `client_id`, `client_secret`, `refresh_token`, and
    `auth_type` lived at the config root. Starting in v2.8.0 they are
    nested under `credentials` with a discriminated `oneOf` so that the
    platform's OAuth credential injection only fires for the OAuth
    variant (auth_type == "Client") and not for the Manual variant.

    Existing connections are migrated to `credentials.auth_type = "Client"`
    (OAuth) because the platform was already injecting Airbyte's own
    credentials for every prior connection.
    """

    message_repository: MessageRepository = InMemoryMessageRepository()

    @classmethod
    def should_migrate(cls, config: Mapping[str, Any]) -> bool:
        """Return True when the config still has credentials at the root level."""
        return "credentials" not in config and "client_id" in config

    @classmethod
    def transform(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        config["credentials"] = {
            "auth_type": config.pop("auth_type", "Client"),
            "client_id": config.pop("client_id", ""),
            "client_secret": config.pop("client_secret", ""),
            "refresh_token": config.pop("refresh_token", ""),
        }
        return config

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        migrated_config = cls.transform(config)
        source.write_config(migrated_config, config_path)
        return migrated_config

    @classmethod
    def migrate(cls, args: List[str], source: Source) -> None:
        config_path = AirbyteEntrypoint(source).extract_config(args)
        if config_path:
            config = source.read_config(config_path)
            if cls.should_migrate(config):
                cls.modify_and_save(config_path, source, config)
                emit_configuration_as_airbyte_control_message(config)
