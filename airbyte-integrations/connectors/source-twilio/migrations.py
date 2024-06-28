import logging
from typing import Any, List, Mapping

import requests
from airbyte_cdk.config_observation import create_connector_config_control_message
from airbyte_cdk.entrypoint import AirbyteEntrypoint
from airbyte_cdk.sources import Source
from airbyte_cdk.utils import AirbyteTracedException
from airbyte_protocol.models import FailureType

logger = logging.getLogger("airbyte_logger")


class MigrateDataCenter:
    """
    This class stands for migrating the state at runtime,
    Set stream state partition property in config based on credential type.
    """

    STREAMS = ["calls"]

    def migrate_state(cls, stream_name, state: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        This method migrates the state.
        Args:
        - stream_name (str): The stream name.
        - state (Mapping[str, Any]): The state to migrate.
        Returns:
        - Mapping[str, Any]: The migrated state.
        """
        if stream_name in cls.STREAMS:
            if "partition" in state:
                return state
            return {"partition": {"data_center": "us1"}, "cursor": state}
        return state

    @classmethod
    def migrate(cls, args: List[str], source: Source) -> None:
        """
        Orchestrates the migration process.
        Args:
        - args (List[str]): List of command-line arguments.
        - source (Source): The data source.
        """
        config_path = AirbyteEntrypoint(source).extract_config(args)
        if config_path:
            config = source.read_config(config_path)
            cls.emit_control_message(cls.modify_and_save(config_path, source, config))
