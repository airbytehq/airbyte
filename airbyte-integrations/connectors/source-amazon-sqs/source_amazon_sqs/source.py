#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


import json
from datetime import datetime
from typing import Dict, Generator

import boto3
from botocore.exceptions import ClientError

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
from airbyte_cdk.sources.source import Source


class SourceAmazonSqs(Source):
    def delete_message(self, message):
        try:
            message.delete()
        except ClientError:
            raise Exception("Couldn't delete message: %s - does your IAM user have sqs:DeleteMessage?", message.message_id)

    def change_message_visibility(self, message, visibility_timeout):
        try:
            message.change_visibility(VisibilityTimeout=visibility_timeout)
        except ClientError:
            raise Exception(
                "Couldn't change message visibility: %s - does your IAM user have sqs:ChangeMessageVisibility?", message.message_id
            )

    def parse_queue_name(self, url: str) -> str:
        return url.rsplit("/", 1)[-1]

    def check(self, logger: AirbyteLogger, config: json) -> AirbyteConnectionStatus:
        try:
            if "max_batch_size" in config:
                # Max batch size must be between 1 and 10
                if config["max_batch_size"] > 10 or config["max_batch_size"] < 1:
                    raise Exception("max_batch_size must be between 1 and 10")
            if "max_wait_time" in config:
                # Max wait time must be between 1 and 20
                if config["max_wait_time"] > 20 or config["max_wait_time"] < 1:
                    raise Exception("max_wait_time must be between 1 and 20")

            # Required propeties
            queue_url = config["queue_url"]
            logger.debug("Amazon SQS Source Config Check - queue_url: " + queue_url)
            queue_region = config["region"]
            logger.debug("Amazon SQS Source Config Check - region: " + queue_region)
            # Senstive Properties
            access_key = config["access_key"]
            logger.debug("Amazon SQS Source Config Check - access_key (ends with): " + access_key[-1])
            secret_key = config["secret_key"]
            logger.debug("Amazon SQS Source Config Check - secret_key (ends with): " + secret_key[-1])

            logger.debug("Amazon SQS Source Config Check - Starting connection test ---")
            session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=queue_region)
            sqs = session.resource("sqs")
            queue = sqs.Queue(url=queue_url)
            if hasattr(queue, "attributes"):
                logger.debug("Amazon SQS Source Config Check - Connection test successful ---")
                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(status=Status.FAILED, message="Amazon SQS Source Config Check - Could not connect to queue")
        except ClientError as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"Amazon SQS Source Config Check - Error in AWS Client: {str(e)}")
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"Amazon SQS Source Config Check - An exception occurred: {str(e)}"
            )

    def discover(self, logger: AirbyteLogger, config: json) -> AirbyteCatalog:
        streams = []

        # Get the queue name by getting substring after last /
        stream_name = self.parse_queue_name(config["queue_url"])
        logger.debug("Amazon SQS Source Stream Discovery - stream is: " + stream_name)

        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"id": {"type": "string"}, "body": {"type": "string"}, "attributes": {"type": ["object", "null"]}},
        }
        streams.append(AirbyteStream(name=stream_name, json_schema=json_schema, supported_sync_modes=["full_refresh"]))
        return AirbyteCatalog(streams=streams)

    def read(
        self, logger: AirbyteLogger, config: json, catalog: ConfiguredAirbyteCatalog, state: Dict[str, any]
    ) -> Generator[AirbyteMessage, None, None]:
        stream_name = self.parse_queue_name(config["queue_url"])
        logger.debug("Amazon SQS Source Read - stream is: " + stream_name)

        # Required propeties
        queue_url = config["queue_url"]
        queue_region = config["region"]
        delete_messages = config["delete_messages"]

        # Optional Properties
        max_batch_size = config.get("max_batch_size", 10)
        max_wait_time = config.get("max_wait_time", 20)
        visibility_timeout = config.get("visibility_timeout")
        attributes_to_return = config.get("attributes_to_return")
        if attributes_to_return is None:
            attributes_to_return = ["All"]
        else:
            attributes_to_return = attributes_to_return.split(",")

        # Senstive Properties
        access_key = config["access_key"]
        secret_key = config["secret_key"]

        logger.debug("Amazon SQS Source Read - Creating SQS connection ---")
        session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=queue_region)
        sqs = session.resource("sqs")
        queue = sqs.Queue(url=queue_url)
        logger.debug("Amazon SQS Source Read - Connected to SQS Queue ---")
        timed_out = False
        while not timed_out:
            try:
                logger.debug("Amazon SQS Source Read - Beginning message poll ---")
                messages = queue.receive_messages(
                    MessageAttributeNames=attributes_to_return, MaxNumberOfMessages=max_batch_size, WaitTimeSeconds=max_wait_time
                )

                if not messages:
                    logger.debug("Amazon SQS Source Read - No messages recieved during poll, time out reached ---")
                    timed_out = True
                    break

                for msg in messages:
                    logger.debug("Amazon SQS Source Read - Message recieved: " + msg.message_id)
                    if visibility_timeout:
                        logger.debug("Amazon SQS Source Read - Setting message visibility timeout: " + msg.message_id)
                        self.change_message_visibility(msg, visibility_timeout)
                        logger.debug("Amazon SQS Source Read - Message visibility timeout set: " + msg.message_id)

                    data = {
                        "id": msg.message_id,
                        "body": msg.body,
                        "attributes": msg.message_attributes,
                    }

                    # TODO: Support a 'BATCH OUTPUT' mode that outputs the full batch in a single AirbyteRecordMessage
                    yield AirbyteMessage(
                        type=Type.RECORD,
                        record=AirbyteRecordMessage(stream=stream_name, data=data, emitted_at=int(datetime.now().timestamp()) * 1000),
                    )
                    if delete_messages:
                        logger.debug("Amazon SQS Source Read - Deleting message: " + msg.message_id)
                        self.delete_message(msg)
                        logger.debug("Amazon SQS Source Read - Message deleted: " + msg.message_id)
                        # TODO: Delete messages in batches to reduce amount of requests?

            except ClientError as error:
                raise Exception("Error in AWS Client: " + str(error))
