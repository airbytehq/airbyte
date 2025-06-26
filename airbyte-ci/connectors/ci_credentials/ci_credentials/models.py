#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from __future__ import (  # Used to evaluate type hints at runtime, a NameError: name 'RemoteSecret' is not defined is thrown otherwise
    annotations,
)

from dataclasses import dataclass


DEFAULT_SECRET_FILE = "config"


@dataclass
class Secret:
    connector_name: str
    configuration_file_name: str
    value: str

    @property
    def name(self) -> str:
        return self.generate_secret_name(self.connector_name, self.configuration_file_name)

    @staticmethod
    def generate_secret_name(connector_name: str, configuration_file_name: str) -> str:
        """
        Generates an unique GSM secret name.
        Format of secret name: SECRET_<CAPITAL_CONNECTOR_NAME>_<OPTIONAL_UNIQUE_FILENAME_PART>__CREDS
        Examples:
            1. connector_name: source-linnworks, filename: dsdssds_a-b---_---_config.json
                => SECRET_SOURCE-LINNWORKS_DSDSSDS_A-B__CREDS
            2. connector_name: source-s3, filename: config.json
                => SECRET_SOURCE-LINNWORKS__CREDS
        """
        name_parts = ["secret", connector_name]
        filename_wo_ext = configuration_file_name.replace(".json", "")
        if filename_wo_ext != DEFAULT_SECRET_FILE:
            name_parts.append(filename_wo_ext.replace(DEFAULT_SECRET_FILE, "").strip("_-"))
        name_parts.append("_creds")
        return "_".join(name_parts).upper()

    @property
    def directory(self) -> str:
        if self.connector_name == "base-normalization":
            return f"airbyte-integrations/bases/{self.connector_name}/secrets"
        else:
            return f"airbyte-integrations/connectors/{self.connector_name}/secrets"


@dataclass
class RemoteSecret(Secret):
    enabled_version: str

    @classmethod
    def from_secret(cls, secret: Secret, enabled_version: str) -> RemoteSecret:
        return RemoteSecret(secret.connector_name, secret.configuration_file_name, secret.value, enabled_version)
