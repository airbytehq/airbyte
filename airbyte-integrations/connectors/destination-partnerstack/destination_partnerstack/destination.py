#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type

from logging import getLogger

from destination_partnerstack.client import PartnerStackClient

logger = getLogger("airbyte")


class DestinationPartnerstack(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:
        client = PartnerStackClient(**config)
        for message in input_messages:
            if message.type == Type.STATE:
                yield message
            elif message.type == Type.RECORD:
                response = client.write(message.record.data)
                if response.status_code != 200:
                    logger.error({"record": message.record.data, "error": response.json()})
            else:
                continue

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            client = PartnerStackClient(**config)
            response = client.list()
            if response.status_code != 200:
                raise Exception("Invalid connection parameters.")
            else:
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
