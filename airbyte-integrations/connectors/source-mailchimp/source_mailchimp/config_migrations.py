#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import logging
import os
import stat
from typing import Any, List, Mapping

import requests
from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.models import AirbyteLogMessage, AirbyteMessage, Level, Type
from airbyte_cdk.sources import Source
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType

logger = logging.getLogger("airbyte_logger")


class MigrateDataCenter:
    """
    This class stands for migrating the config at runtime,
    Set data_center property in config based on credential type.
    """

    @classmethod
    def get_data_center_location(cls, config: Mapping[str, Any]) -> Mapping[str, Any]:
        if config.get("credentials", {}).get("auth_type") == "apikey":
            data_center = config["credentials"]["apikey"].split("-").pop()
        else:
            data_center = cls.get_oauth_data_center(config["credentials"]["access_token"])
        config["data_center"] = data_center
        return config

    @staticmethod
    def get_oauth_data_center(access_token: str) -> str:
        """
        Every Mailchimp API request must be sent to a specific data center.
        The data center is already embedded in API keys, but not OAuth access tokens.
        This method retrieves the data center for OAuth credentials.
        """
        response = requests.get("https://login.mailchimp.com/oauth2/metadata", headers={"Authorization": "OAuth {}".format(access_token)})

        # Requests to this endpoint will return a 200 status code even if the access token is invalid.
        error = response.json().get("error")
        if error == "invalid_token":
            raise AirbyteTracedException(
                failure_type=FailureType.config_error,
                internal_message=error,
                message="The access token you provided was invalid. Please check your credentials and try again.",
            )
        return response.json()["dc"]

    @classmethod
    def modify_and_save(cls, config_path: str, source: Source, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Modifies the configuration and then saves it back to the source.

        Args:
        - config_path (str): The path where the configuration is stored.
        - source (Source): The data source.
        - config (Mapping[str, Any]): The current configuration.

        Returns:
        - Mapping[str, Any]: The updated configuration.
        """
        user_id = os.getuid()
        group_id = os.getgid()
        message = f"Executing as User ID: {user_id}, Group ID: {group_id}"
        print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=message)).json())

        migrated_config = cls.get_data_center_location(config)

        # Check and print the permissions of the directory containing config_path
        dir_path = os.path.dirname(config_path)
        try:
            dir_stat = os.stat(dir_path)
            dir_permissions = stat.filemode(dir_stat.st_mode)
            dir_owner = dir_stat.st_uid
            dir_group = dir_stat.st_gid
            message = f"Directory permissions for {dir_path}: {dir_permissions}, Owner: {dir_owner}, Group: {dir_group}"
            print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=message)).json())
        except FileNotFoundError:
            error_message = f"Directory not found: {dir_path}"
            print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.ERROR, message=error_message)).json())
            raise

        # Check and print the permissions of config_path
        try:
            file_stat = os.stat(config_path)
            permissions = stat.filemode(file_stat.st_mode)
            owner = file_stat.st_uid
            group = file_stat.st_gid
            message = f"File permissions for {config_path}: {permissions}, Owner: {owner}, Group: {group}"
            print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=message)).json())
        except FileNotFoundError:
            error_message = f"File not found: {config_path}"
            print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.ERROR, message=error_message)).json())
            raise

        try:
            if os.access(config_path, os.W_OK):
                message = f"Everything seems fine writing to <3: {config_path}"
                print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=message)).json())
            else:
                error_message = f"No write permission for config path, this will fail!!: {config_path}"
                print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.ERROR, message=error_message)).json())
            source.write_config(migrated_config, config_path)
        except PermissionError as e:
            error_message = f"Permission denied when trying to write to {config_path}: {e}"
            print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.ERROR, message=error_message)).json())

            # sets both the user and group of config_path to 0 (root).
            os.chown(config_path, 0, 0)
            message = f"Trying again to write to : {config_path}"
            print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=message)).json())
            source.write_config(migrated_config, config_path)
            # raise e
        return migrated_config

    @classmethod
    def emit_control_message(cls, migrated_config: Mapping[str, Any]) -> None:
        """
        Emits the control messages related to configuration migration.

        Args:
        - migrated_config (Mapping[str, Any]): The migrated configuration.
        """
        print(create_connector_config_control_message(migrated_config).json(exclude_unset=True))

    @classmethod
    def migrate(cls, args: List[str], source: Source) -> None:
        """
        Orchestrates the configuration migration process.

        It first checks if the `--config` argument is provided, and if so,
        determines whether migration is needed, and then performs the migration
        if required.

        Args:
        - args (List[str]): List of command-line arguments.
        - source (Source): The data source.
        """
        config_path = AirbyteEntrypoint(source).extract_config(args)
        message = f"The path received was {config_path}"
        print(AirbyteMessage(type=Type.LOG, log=AirbyteLogMessage(level=Level.INFO, message=message)).json())
        if config_path:
            config = source.read_config(config_path)
            cls.emit_control_message(cls.modify_and_save(config_path, source, config))
