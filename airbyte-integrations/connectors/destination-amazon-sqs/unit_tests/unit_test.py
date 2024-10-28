#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
import logging
import time
from typing import Any, Mapping

import boto3
from airbyte_cdk.models import AirbyteMessage, ConfiguredAirbyteCatalog, Status
from destination_amazon_sqs import DestinationAmazonSqs

# from airbyte_cdk.sources.source import Source
from moto import mock_iam, mock_sqs
from moto.core import set_initial_no_auth_action_count


@mock_iam
def create_user_with_all_permissions():
    client = boto3.client("iam", region_name="eu-west-1")
    client.create_user(UserName="test_user1")

    policy_document = {
        "Version": "2012-10-17",
        "Statement": [{"Effect": "Allow", "Action": ["sqs:*"], "Resource": "*"}],
    }

    client.put_user_policy(
        UserName="test_user1",
        PolicyName="policy1",
        PolicyDocument=json.dumps(policy_document),
    )

    return client.create_access_key(UserName="test_user1")["AccessKey"]


def create_config(queue_url, queue_region, access_key, secret_key, message_delay):
    return {
        "queue_url": queue_url,
        "region": queue_region,
        "access_key": access_key,
        "secret_key": secret_key,
        "message_delay": message_delay,
    }


def create_fifo_config(queue_url, queue_region, access_key, secret_key, message_group_id, message_delay):
    return {
        "queue_url": queue_url,
        "region": queue_region,
        "access_key": access_key,
        "secret_key": secret_key,
        "message_group_id": message_group_id,
        "message_delay": message_delay,
    }


def create_config_with_body_key(queue_url, queue_region, access_key, secret_key, message_body_key, message_delay):
    return {
        "queue_url": queue_url,
        "region": queue_region,
        "access_key": access_key,
        "secret_key": secret_key,
        "message_body_key": message_body_key,
        "message_delay": message_delay,
    }


def get_catalog() -> Mapping[str, Any]:
    with open("sample_files/configured_catalog.json", "r") as f:
        return json.load(f)


@set_initial_no_auth_action_count(3)
@mock_sqs
@mock_iam
def test_check():
    # Create User
    user = create_user_with_all_permissions()
    # Create Queue
    queue_name = "amazon-sqs-mock-queue"
    queue_region = "eu-west-1"
    client = boto3.client(
        "sqs", aws_access_key_id=user["AccessKeyId"], aws_secret_access_key=user["SecretAccessKey"], region_name=queue_region
    )
    queue_url = client.create_queue(QueueName=queue_name)["QueueUrl"]
    # Create config
    config = create_config(queue_url, queue_region, user["AccessKeyId"], user["SecretAccessKey"], 10)
    # Create AirbyteLogger
    logger = logging.getLogger("airbyte")
    # Create Destination
    destination = DestinationAmazonSqs()
    # Run check
    status = destination.check(logger, config)
    assert status.status == Status.SUCCEEDED

    # Create FIFO queue
    fifo_queue_name = "amazon-sqs-mock-queue.fifo"
    fif_queue_url = client.create_queue(QueueName=fifo_queue_name, Attributes={"FifoQueue": "true"})["QueueUrl"]
    # Create config for FIFO
    fifo_config = create_fifo_config(fif_queue_url, queue_region, user["AccessKeyId"], user["SecretAccessKey"], "fifo-group", 10)
    # Run check
    status = destination.check(logger, fifo_config)
    assert status.status == Status.SUCCEEDED


@set_initial_no_auth_action_count(4)
@mock_sqs
@mock_iam
def test_write():
    # Create User
    user = create_user_with_all_permissions()

    test_message = {
        "type": "RECORD",
        "record": {
            "stream": "ab-airbyte-testing",
            "data": {"id": "ba0f237b-abf5-41ae-9d94-1dbd346f38dd", "body": "test 1", "attributes": None},
            "emitted_at": 1633881878000,
        },
    }
    ab_message = AirbyteMessage(**test_message)

    # Common params
    message_delay = 1
    queue_region = "eu-west-1"

    # Standard Queue Test
    print("## Starting standard queue test ##")
    # Create Queue
    queue_name = "amazon-sqs-mock-queue"
    client = boto3.client(
        "sqs", aws_access_key_id=user["AccessKeyId"], aws_secret_access_key=user["SecretAccessKey"], region_name=queue_region
    )
    queue_url = client.create_queue(QueueName=queue_name)["QueueUrl"]
    # Create config
    config = create_config(queue_url, queue_region, user["AccessKeyId"], user["SecretAccessKey"], message_delay)
    # Create ConfiguredAirbyteCatalog
    catalog = ConfiguredAirbyteCatalog(streams=get_catalog()["streams"])
    # Create Destination
    destination = DestinationAmazonSqs()
    # Send messages using write()
    for message in destination.write(config, catalog, [ab_message]):
        print(f"Message Sent with delay of {message_delay} seconds")
    # Listen for messages for max 20 seconds
    timeout = time.time() + 20
    print("Listening for messages.")
    while True:
        message_received = client.receive_message(QueueUrl=queue_url)
        if message_received.get("Messages"):
            print("Message received.")
            message_body = json.loads(message_received["Messages"][0]["Body"])
            # Compare the body of the received message, with the body of the message we sent
            if message_body == test_message["record"]["data"]:
                print("Received message matches for standard queue write.")
                assert True
                break
            else:
                continue
        if time.time() > timeout:
            print("Timed out waiting for message after 20 seconds.")
            assert False

    # Standard Queue with a Message Key Test
    print("## Starting body key queue test ##")
    # Create Queue
    key_queue_name = "amazon-sqs-mock-queue-key"
    key_queue_url = client.create_queue(QueueName=key_queue_name)["QueueUrl"]
    # Create config
    message_body_key = "body"
    key_config = create_config_with_body_key(
        key_queue_url, queue_region, user["AccessKeyId"], user["SecretAccessKey"], message_body_key, message_delay
    )
    # Send messages using write()
    for message in destination.write(key_config, catalog, [ab_message]):
        print(f"Message Sent with delay of {message_delay} seconds")
    # Listen for messages for max 20 seconds
    timeout = time.time() + 20
    print("Listening for messages.")
    while True:
        message_received = client.receive_message(QueueUrl=key_queue_url)
        if message_received.get("Messages"):
            print("Message received.")
            message_body = message_received["Messages"][0]["Body"]
            # Compare the body of the received message, with the body of the message we sent
            if message_body == test_message["record"]["data"][message_body_key]:
                print("Received message matches for body key queue write.")
                assert True
                break
            else:
                continue
        if time.time() > timeout:
            print("Timed out waiting for message after 20 seconds.")
            assert False

    # FIFO Queue Test
    print("## Starting FIFO queue test ##")
    # Create Queue
    fifo_queue_name = "amazon-sqs-mock-queue.fifo"
    fifo_queue_url = client.create_queue(QueueName=fifo_queue_name, Attributes={"FifoQueue": "true"})["QueueUrl"]
    # Create config
    fifo_config = create_fifo_config(
        fifo_queue_url, queue_region, user["AccessKeyId"], user["SecretAccessKey"], "fifo-group", message_delay
    )
    # Send messages using write()
    for message in destination.write(fifo_config, catalog, [ab_message]):
        print(f"Message Sent with delay of {message_delay} seconds")
    # Listen for messages for max 20 seconds
    timeout = time.time() + 20
    print("Listening for messages.")
    while True:
        message_received = client.receive_message(QueueUrl=fifo_queue_url)
        if message_received.get("Messages"):
            print("Message received.")
            message_body = json.loads(message_received["Messages"][0]["Body"])
            # Compare the body of the received message, with the body of the message we sent
            if message_body == test_message["record"]["data"]:
                print("Received message matches for FIFO queue write.")
                assert True
                break
            else:
                continue
        if time.time() > timeout:
            print("Timed out waiting for message after 20 seconds.")
            assert False
