#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator

import boto3
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (
    AirbyteCatalog,
    AirbyteConnectionStatus,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    ConfiguredAirbyteCatalog,
    Status,
    Type,
)
from airbyte_cdk.sources import Source
from botocore.exceptions import ClientError


class SourceAmazonSqs(Source):

    def delete_message(self, message):
        try:
            message.delete()
            # TODO: Info logging for deleted messages?
        except ClientError as error:
            print("Couldn't delete message: %s", message.message_id)
            # TODO: Handle errors

    def change_message_visibility(self, message, visibility_timeout):
        try:
            message.change_visibility(VisibilityTimeout=visibility_timeout)
        except ClientError as error:
            print("Couldn't change message visibility: %s", message.message_id)
            # TODO: Handle errors

    def parse_queue_name(self, url: str) -> str:
        return url.rsplit('/', 1)[-1]

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        try:

            optional_properties = ["MAX_BATCH_SIZE",
                                   "MAX_WAIT_TIME", "ATTRIBUTES_TO_RETURN"]
            if "MAX_BATCH_SIZE" in config:
                # Max batch size must be between 1 and 10
                if config["MAX_BATCH_SIZE"] > 10 or config["MAX_BATCH_SIZE"] < 1:
                    raise Exception("MAX_BATCH_SIZE must be between 1 and 10")
            if "MAX_WAIT_TIME" in config:
                # Max wait time must be between 1 and 20
                if config["MAX_WAIT_TIME"] > 20 or config["MAX_WAIT_TIME"] < 1:
                    raise Exception("MAX_WAIT_TIME must be between 1 and 20")

            # Required propeties
            queue_url = config["QUEUE_URL"]
            queue_region = config["REGION"]
            # Senstive Properties
            access_key = config["ACCESS_KEY"]
            secret_key = config["SECRET_KEY"]

            session = boto3.Session(
                aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=queue_region)
            sqs = session.resource("sqs")
            queue = sqs.Queue(url=queue_url)
            # This will fail if we are not connected to the Queue (AWS.SimpleQueueService.NonExistentQueue)
            attrs = queue.attributes
            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {str(e)}")

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        streams = []

        # Get the queue name by getting substring after last /
        stream_name = self.parse_queue_name(config["QUEUE_URL"])

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"id": {"type": "integer"}, "body": {"type": "string"}, "attributes": {"type": "object"}},
        }
        streams.append(AirbyteStream(
            name=stream_name, json_schema=json_schema, supported_sync_modes=["FULL_REFRESH"]))
        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        stream_name = self.parse_queue_name(config["QUEUE_URL"])

        # Required propeties
        queue_url = config["QUEUE_URL"]
        queue_region = config["REGION"]
        delete_messages = config["DELETE_MESSAGES"]

        # Optional Properties
        max_batch_size = config.get("MAX_BATCH_SIZE", 10)
        max_wait_time = config.get("MAX_WAIT_TIME", 20)
        visibility_timeout = config.get("VISIBILITY_TIMEOUT")
        attributes_to_return = config.get("ATTRIBUTES_TO_RETURN")
        if attributes_to_return is None:
            attributes_to_return = ["All"]
        else:
            attributes_to_return = attributes_to_return.split(",")

        # Senstive Properties
        access_key = config["ACCESS_KEY"]
        secret_key = config["SECRET_KEY"]

        session = boto3.Session(aws_access_key_id=access_key,
                                aws_secret_access_key=secret_key, region_name=queue_region)
        sqs = session.resource("sqs")
        queue = sqs.Queue(url=queue_url)

        timed_out = False
        while not timed_out:
            try:
                messages = queue.receive_messages(
                    MessageAttributeNames=attributes_to_return, MaxNumberOfMessages=max_batch_size, WaitTimeSeconds=max_wait_time
                )

                if not messages:
                    timed_out = True
                    break

                for msg in messages:
                    if visibility_timeout:
                        self.change_message_visibility(msg, visibility_timeout)

                    data = {
                        "id": msg.message_id,
                        "body": msg.body,
                        "attributes": msg.message_attributes,
                    }
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(
                            datetime.now().timestamp()) * 1000),
                    )
                    if delete_messages:
                        self.delete_message(msg)
                        # TODO: Delete messages in batches to reduce amount of requests?

            except ClientError as error:
                print("Couldn't receive messages from queue: %s", queue)
                raise error
