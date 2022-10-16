#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import logging
import os
from typing import Any, Dict, Iterable, List, Mapping, Type

from airbyte_cdk.models import AirbyteCatalog, AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status
from airbyte_cdk.sources.source import BaseSource
from airbyte_cdk.sources.utils.catalog_helpers import CatalogHelper

from .singer_helpers import Catalogs, SingerHelper, SyncModeInfo


class ConfigContainer(Dict[str, Any]):
    config_path: str

    def __init__(self, config, config_path):
        super().__init__(config)
        self.config_path = config_path


class SingerSource(BaseSource[ConfigContainer, str, str]):
    def configure(self, config: Mapping[str, Any], temp_dir: str) -> ConfigContainer:
        """
        Persist raw_config in temporary directory to run the Source job
        This can be overridden if extra temporary files need to be persisted in the temp dir
        """
        config_path = os.path.join(temp_dir, "config.json")
        config = ConfigContainer(self.transform_config(config), config_path)
        self.write_config(config, config_path)
        return config

    # Can be overridden to change an input config
    def transform_config(self, config: Mapping[str, Any]) -> Mapping[str, Any]:
        """
        Singer source may need to adapt the Config object for the singer tap specifics
        """
        return config

    def read_catalog(self, catalog_path: str) -> str:
        """
        Since singer source don't need actual catalog object, we override this to return path only
        """
        return catalog_path

    def read_state(self, state_path: str) -> str:
        """
        Since singer source don't need actual state object, we override this to return path only
        """
        return state_path

    def check_config(self, logger: logging.Logger, config_path: str, config: ConfigContainer) -> AirbyteConnectionStatus:
        """
        Some Singer source may perform check using config_path or config to
        tests if the input configuration can be used to successfully connect to the integration
        """
        raise NotImplementedError

    def discover_cmd(self, logger: logging.Logger, config_path: str) -> str:
        """
        Returns the command used to run discovery in the singer tap. For example, if the bash command used to invoke the singer tap is `tap-postgres`,
        and the config JSON lived in "/path/config.json", this method would return "tap-postgres --config /path/config.json"
        """
        raise NotImplementedError

    def read_cmd(self, logger: logging.Logger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        """
        Returns the command used to read data from the singer tap. For example, if the bash command used to invoke the singer tap is `tap-postgres`,
        and the config JSON lived in "/path/config.json", and the catalog was in "/path/catalog.json",
        this method would return "tap-postgres --config /path/config.json --catalog /path/catalog.json"
        """
        raise NotImplementedError

    def _discover_internal(self, logger: logging.Logger, config_path: str) -> Catalogs:
        cmd = self.discover_cmd(logger, config_path)
        catalogs = SingerHelper.get_catalogs(
            logger, cmd, self.get_sync_mode_overrides(), self.get_primary_key_overrides(), self.get_excluded_streams()
        )
        return catalogs

    def check(self, logger: logging.Logger, config: ConfigContainer) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the integration
        """
        return self.check_config(logger, config.config_path, config)

    def discover(self, logger: logging.Logger, config: ConfigContainer) -> AirbyteCatalog:
        """
        Implements the parent class discover method.
        """
        return self._discover_internal(logger, config.config_path).airbyte_catalog

    def read(self, logger: logging.Logger, config: ConfigContainer, catalog_path: str, state_path: str = None) -> Iterable[AirbyteMessage]:
        """
        Implements the parent class read method.
        """
        catalogs = self._discover_internal(logger, config.config_path)
        masked_airbyte_catalog = ConfiguredAirbyteCatalog.parse_obj(self.read_config(catalog_path))
        selected_singer_catalog_path = SingerHelper.create_singer_catalog_with_selection(masked_airbyte_catalog, catalogs.singer_catalog)

        read_cmd = self.read_cmd(logger, config.config_path, selected_singer_catalog_path, state_path)
        return SingerHelper.read(logger, read_cmd)

    def get_sync_mode_overrides(self) -> Dict[str, SyncModeInfo]:
        """
        The Singer Spec outlines a way for taps to declare in their catalog that their streams support incremental sync (valid-replication-keys,
        forced-replication-method, and others). However, many taps which are incremental don't actually declare that via the catalog, and just
        use their input state to perform an incremental sync without giving any hints to the user. An Airbyte Connector built on top of such a
        Singer Tap cannot automatically detect which streams are full refresh or incremental or what their cursors are. In those cases the developer
        needs to manually specify information about the sync modes.

        This method provides a way of doing that: the dict of stream names to SyncModeInfo returned from this method will be used to override each
        stream's sync mode information in the Airbyte Catalog output from the discover method. Only set fields provided in the SyncModeInfo are used.
        If a SyncModeInfo field is not set, it will not be overridden in the output catalog.

        :return: A dict from stream name to the sync modes that should be applied to this stream.
        """
        return {}

    def get_primary_key_overrides(self) -> Dict[str, List[str]]:
        """
        Similar to get_sync_mode_overrides but for primary keys.

        :return: A dict from stream name to the list of primary key fields for the stream.
        """
        return {}

    def get_excluded_streams(self) -> List[str]:
        """
        This method provide ability to exclude some streams from catalog

        :return: A list of excluded stream names
        """
        return []


class BaseSingerSource(SingerSource):
    force_full_refresh = False

    def check_config(self, logger: logging.Logger, config_path: str, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            self.try_connect(logger, config)
        except self.api_error as err:
            logger.error(f"Exception while connecting to {self.tap_name}: {err}")
            # this should be in UI
            error_msg = f"Unable to connect to {self.tap_name} with the provided credentials. Error: {err}"
            return AirbyteConnectionStatus(status=Status.FAILED, message=error_msg)
        return AirbyteConnectionStatus(status=Status.SUCCEEDED)

    def discover_cmd(self, logger: logging.Logger, config_path: str) -> str:
        return f"{self.tap_cmd} --config {config_path} --discover"

    def read_cmd(self, logger: logging.Logger, config_path: str, catalog_path: str, state_path: str = None) -> str:
        state_path = None if self.force_full_refresh else state_path
        args = {"--config": config_path, "--catalog": catalog_path, "--state": state_path}
        cmd = " ".join([f"{k} {v}" for k, v in args.items() if v is not None])

        return f"{self.tap_cmd} {cmd}"

    def discover(self, logger: logging.Logger, config: ConfigContainer) -> AirbyteCatalog:
        catalog = super().discover(logger, config)
        if self.force_full_refresh:
            return CatalogHelper.coerce_catalog_as_full_refresh(catalog)
        return catalog

    def try_connect(self, logger: logging.Logger, config: Mapping[str, Any]):
        """Test provided credentials, raises self.api_error if something goes wrong"""
        raise NotImplementedError

    @property
    def api_error(self) -> Type[Exception]:
        """Class/Base class of the exception that will be thrown if the tap is misconfigured or service unavailable"""
        raise NotImplementedError

    @property
    def tap_cmd(self) -> str:
        """Tap command"""
        raise NotImplementedError

    @property
    def tap_name(self) -> str:
        """Tap name"""
        raise NotImplementedError
