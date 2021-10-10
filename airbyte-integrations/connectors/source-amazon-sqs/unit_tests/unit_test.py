#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Mapping, Dict

from airbyte_cdk.sources.source import Source
from airbyte_cdk.logger import AirbyteLogger
from airbyte_cdk.models import (ConfiguredAirbyteCatalog, Status)

from source_amazon_sqs import SourceAmazonSqs


import boto3
from moto import mock_sqs, mock_iam
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


def create_config(queue_url, access_key, secret_key, queue_region, delete_message):
    return {
        "DELETE_MESSAGES": delete_message,
        "QUEUE_URL": queue_url,
        "REGION": queue_region,
        "ACCESS_KEY": access_key,
        "SECRET_KEY": secret_key,
        "MAX_WAIT_TIME": 2
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
    client = boto3.client("sqs",
                          aws_access_key_id=user["AccessKeyId"],
                          aws_secret_access_key=user["SecretAccessKey"],
                          region_name=queue_region)

    queue_url = client.create_queue(QueueName=queue_name)["QueueUrl"]
    # Create config
    config = create_config(
        queue_url,
        user["AccessKeyId"],
        user["SecretAccessKey"],
        queue_region,
        False)
    # Create AirbyteLogger
    logger = AirbyteLogger()
    # Create Source
    source = SourceAmazonSqs()
    # Run check
    status = source.check(logger, config)
    assert status.status == Status.SUCCEEDED

@mock_sqs
def test_discover():
    # Create Queue
    queue_name = "amazon-sqs-mock-queue"
    queue_region = "eu-west-1"
    client = boto3.client("sqs",
                          region_name=queue_region)
    queue_url = client.create_queue(QueueName=queue_name)["QueueUrl"]
    # Create config
    config = create_config(
        queue_url,
        "xxx",
        "xxx",
        queue_region,
        False)
    # Create AirbyteLogger
    logger = AirbyteLogger()
    # Create Source
    source = SourceAmazonSqs()
    # Run discover
    catalog = source.discover(logger, config)
    assert catalog.streams[0].name == queue_name


@set_initial_no_auth_action_count(3)
@mock_sqs
@mock_iam
def test_read():
    # Create User
    user = create_user_with_all_permissions()
    # Create Queue
    queue_name = "amazon-sqs-mock-queue"
    queue_region = "eu-west-1"
    client = boto3.client("sqs",
                          aws_access_key_id=user["AccessKeyId"],
                          aws_secret_access_key=user["SecretAccessKey"],
                          region_name=queue_region)

    queue_url = client.create_queue(QueueName=queue_name)["QueueUrl"]
    # Create config
    config = create_config(
        queue_url,
        user["AccessKeyId"],
        user["SecretAccessKey"],
        queue_region,
        False)
    # Create ConfiguredAirbyteCatalog
    catalog = ConfiguredAirbyteCatalog(streams=get_catalog()['streams'])
    # Create AirbyteLogger
    logger = AirbyteLogger()
    # Create State
    state = Dict[str, any]
    # Create Source
    source = SourceAmazonSqs()
    # Send test message
    test_message = "UNIT_TEST_MESSAGE"
    client.send_message(QueueUrl=queue_url, MessageBody=test_message)
    # Run read
    for message in source.read(logger, config, catalog, state):
        record = message.record
        stream = record.stream
        assert stream == queue_name
        data = record.data
        data_body = data["body"]
        assert data_body == test_message
