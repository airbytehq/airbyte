#
# Copyright (c) 2024 Airbyte, Inc., all rights reserved.
#
from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping
from typing import Any

from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status
from destination_deepset.api import DeepsetCloudApi
from destination_deepset.models import DeepsetCloudConfig
from destination_deepset.writer import DeepsetCloudFileWriter


class DestinationDeepset(Destination):
    def get_deepset_cloud_api(self, config: Mapping[str, Any]) -> DeepsetCloudApi:
        deepset_cloud_config = DeepsetCloudConfig.parse_obj(config)
        return DeepsetCloudApi(deepset_cloud_config)

    def write(
        self,
        config: Mapping[str, Any],
        configured_catalog: ConfiguredAirbyteCatalog,
        input_messages: Iterable[AirbyteMessage],
    ) -> Iterable[AirbyteMessage]:
        """
        TODO
        Reads the input stream of messages, config, and catalog to write data to the destination.

        This method returns an iterable (typically a generator of AirbyteMessages via yield) containing state messages received
        in the input message stream. Outputting a state message means that every AirbyteRecordMessage which came before it has been
        successfully persisted to the destination. This is used to ensure fault tolerance in the case that a sync fails before fully completing,
        then the source is given the last state message output from this method as the starting point of the next sync.

        :param config: dict of JSON configuration matching the configuration declared in spec.json
        :param configured_catalog: The Configured Catalog describing the schema of the data being received and how it should be persisted in the
                                    destination
        :param input_messages: The stream of input messages received from the source
        :return: Iterable of AirbyteStateMessages wrapped in AirbyteMessage structs
        """

        deepset_cloud_api = self.get_deepset_cloud_api(config)
        deepset_cloud_file_writer = DeepsetCloudFileWriter(deepset_cloud_api)

        for message in input_messages:
            yield deepset_cloud_file_writer.write(message)

        # @todo[abraham]: We need to do something with the configured catalog but I am not sure what

    def check(self, logger: logging.Logger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        deepset_cloud_api = self.get_deepset_cloud_api(config)

        if deepset_cloud_api.health_check():
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)

        return AirbyteConnectionStatus(status=Status.FAILED, message="Connection is down.")
