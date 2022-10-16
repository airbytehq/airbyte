#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


import json
from typing import Any, Iterable, Mapping
from uuid import uuid4

import boto3
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type
from botocore.exceptions import ClientError


class DestinationAmazonSqs(Destination):
    def queue_is_fifo(self, url: str) -> bool:
        return url.endswith(".fifo")

    def parse_queue_name(self, url: str) -> str:
        return url.rsplit("/", 1)[-1]

    def send_single_message(self, queue, message) -> dict:
        return queue.send_message(**message)

    def build_sqs_message(self, record, message_body_key=None):
        data = None
        if message_body_key:
            data = record.data.get(message_body_key)
            if data is None:
                raise Exception("Message had no attribute of the configured Message Body Key: " + message_body_key)
        else:
            data = json.dumps(record.data)

        message = {"MessageBody": data}

        return message

    def add_attributes_to_message(self, record, message):
        attributes = {"airbyte_emitted_at": {"StringValue": str(record.emitted_at), "DataType": "String"}}
        message["MessageAttributes"] = attributes
        return message

    def set_message_delay(self, message, message_delay):
        message["DelaySeconds"] = message_delay
        return message

    # MessageGroupID and MessageDeduplicationID are required properties for FIFO queues
    # https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_SendMessage.html
    def set_message_fifo_properties(self, message, message_group_id, use_content_dedupe=False):
        # https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/using-messagegroupid-property.html
        if not message_group_id:
            raise Exception("Failed to build message - Message Group ID is required for FIFO queues")
        else:
            message["MessageGroupId"] = message_group_id
        # https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/using-messagededuplicationid-property.html
        if not use_content_dedupe:
            message["MessageDeduplicationId"] = str(uuid4())
        # TODO: Support getting MessageDeduplicationId from a key in the record
        # if message_dedupe_id:
        #     message['MessageDeduplicationId'] = message_dedupe_id
        return message

    # TODO: Support batch send
    # def send_batch_messages(messages, queue):
    #     entry = {
    #         'Id': "1",
    #         'MessageBody': str(record.data),
    #     }
    #     response = queue.send_messages(Entries=messages)
    #     if 'Successful' in response:
    #         for status in response['Successful']:
    #             print("Message sent: " + status['MessageId'])
    #     if 'Failed' in response:
    #         for status in response['Failed']:
    #             print("Message sent: " + status['MessageId'])

    # https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_SendMessage.html
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
    ) -> Iterable[AirbyteMessage]:

        # Required propeties
        queue_url = config["queue_url"]
        queue_region = config["region"]

        # TODO: Implement optional params for batch
        # Optional Properties
        # max_batch_size = config.get("max_batch_size", 10)
        # send_as_batch = config.get("send_as_batch", False)
        message_delay = config.get("message_delay")
        message_body_key = config.get("message_body_key")

        # FIFO Properties
        message_group_id = config.get("message_group_id")

        # Senstive Properties
        access_key = config["access_key"]
        secret_key = config["secret_key"]

        session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=queue_region)
        sqs = session.resource("sqs")
        queue = sqs.Queue(url=queue_url)

        # TODO: Make access/secret key optional, support public access & profiles
        # TODO: Support adding/setting attributes in the UI
        # TODO: Support extract a specific path as message attributes

        for message in input_messages:
            if message.type == Type.RECORD:
                sqs_message = self.build_sqs_message(message.record, message_body_key)

                if message_delay:
                    sqs_message = self.set_message_delay(sqs_message, message_delay)

                sqs_message = self.add_attributes_to_message(message.record, sqs_message)

                if self.queue_is_fifo(queue_url):
                    use_content_dedupe = False if queue.attributes.get("ContentBasedDeduplication") == "false" else "true"
                    self.set_message_fifo_properties(sqs_message, message_group_id, use_content_dedupe)

                self.send_single_message(queue, sqs_message)
            if message.type == Type.STATE:
                yield message

    def check(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> AirbyteConnectionStatus:
        try:
            # Required propeties
            queue_url = config["queue_url"]
            logger.debug("Amazon SQS Destination Config Check - queue_url: " + queue_url)
            queue_region = config["region"]
            logger.debug("Amazon SQS Destination Config Check - region: " + queue_region)

            # Senstive Properties
            access_key = config["access_key"]
            logger.debug("Amazon SQS Destination Config Check - access_key (ends with): " + access_key[-1])
            secret_key = config["secret_key"]
            logger.debug("Amazon SQS Destination Config Check - secret_key (ends with): " + secret_key[-1])

            logger.debug("Amazon SQS Destination Config Check - Starting connection test ---")
            session = boto3.Session(aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name=queue_region)
            sqs = session.resource("sqs")
            queue = sqs.Queue(url=queue_url)
            if hasattr(queue, "attributes"):
                logger.debug("Amazon SQS Destination Config Check - Connection test successful ---")

                if self.queue_is_fifo(queue_url):
                    fifo = queue.attributes.get("FifoQueue", False)
                    if not fifo:
                        raise Exception("FIFO Queue URL set but Queue is not FIFO")

                    message_group_id = config.get("message_group_id")
                    if message_group_id is None:
                        raise Exception("Message Group ID is not set, but is required for FIFO Queues.")

                    # TODO: Support referencing an ID inside the Record to use as de-dupe ID
                    # message_dedupe_key = config.get("message_dedupe_key")
                    # content_dedupe = queue.attributes.get('ContentBasedDeduplication')
                    # if content_dedupe == "false":
                    #     if message_dedupe_id is None:
                    #         raise Exception("You must provide a Message Deduplication ID when ContentBasedDeduplication is not used.")

                return AirbyteConnectionStatus(status=Status.SUCCEEDED)
            else:
                return AirbyteConnectionStatus(
                    status=Status.FAILED, message="Amazon SQS Destination Config Check - Could not connect to queue"
                )
        except ClientError as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"Amazon SQS Destination Config Check - Error in AWS Client: {str(e)}"
            )
        except Exception as e:
            return AirbyteConnectionStatus(
                status=Status.FAILED, message=f"Amazon SQS Destination Config Check - An exception occurred: {str(e)}"
            )
