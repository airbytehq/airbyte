#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, Mapping
import requests
import json
import logging

from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type

from destination_gympass.client import GympassClient

LOGGER = logging.getLogger("airbyte")


class DestinationGympass(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        """
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

        gympass_api_client = GympassClient(**config)
        LOGGER.info(f"Initialised Gympass API client.")
        buffer = []
        for message in input_messages:
            LOGGER.debug(f"message of type: '{message.type}' received..")
            if message.type == Type.STATE:
                # Emitting a state message indicates that all records which came before it have been written to the
                # destination. So we flush the queue to ensure writes happen,
                # then output the state message to indicate it's safe to checkpoint state
                yield message
            elif message.type == Type.RECORD:
                LOGGER.debug(f"Record: {message}")
                record = message.record
                buffer.append(record.data)

                # Flush the buffer if it hits the batch size
                if len(buffer) >= gympass_api_client.BATCH_SIZE:
                    gympass_api_client.batch_write(buffer)
                    buffer = []
            else:
                # ignore other message types for now
                continue

        # Flush any remaining records in the buffer
        if buffer:
            gympass_api_client.batch_write(buffer)

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        """
        Tests if the input configuration can be used to successfully connect to the destination with the needed permissions
            e.g: if a provided API token or password can be used to connect and write to the destination.

        :param logger: Logging object to display debug/info/error to the logs
            (logs will not be accessible via airbyte UI if they are not passed to this logger)
        :param config: Json object containing the configuration of this destination, content of this json is as specified in
        the properties of the spec.json file

        :return: AirbyteConnectionStatus indicating a Success or Failure
        """
        try:
            # Utilize client.py to make a request to the Gympass API
            url = "https://api.wellness.gympass.com/events"

            api_token = config['api_key']

            empty_payload = json.dumps([{}])
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_token}'
            }

            response = requests.request(method="POST", url=url, headers=headers, data=empty_payload)

            # Sending an empty payload to the Gympass API should return a 400 status code with a message indicating
            # that the payload is empty. This is expected for the check as Gympass do not currently expose a health
            # check endpoint, and we do not want to send any data to the API.
            if response.status_code not in [200, 400]:
                return AirbyteConnectionStatus(
                    status=Status.FAILED,
                    message=f"Gympass API response was unsuccessful: {repr(response.text)}. "
                            f"Status code: {response.status_code}."
                )

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
