#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Iterable, Mapping
import threading
import requests
import time

import pika
from airbyte_cdk import AirbyteLogger
from airbyte_cdk.destinations import Destination
from airbyte_cdk.models import AirbyteConnectionStatus, AirbyteMessage, ConfiguredAirbyteCatalog, Status, Type
from pika.adapters.blocking_connection import BlockingConnection
from pika.spec import BasicProperties


_DEFAULT_PORT = 5672
URL = "https://airbyte-testing-new.free.beeceptor.com"

def create_connection(config: Mapping[str, Any]) -> BlockingConnection:
    host = config.get("host")
    port = config.get("port") or _DEFAULT_PORT
    username = config.get("username")
    password = config.get("password")
    virtual_host = config.get("virtual_host", "")
    ssl_enabled = config.get("ssl", False)
    amqp_protocol = "amqp"
    host_url = host
    if ssl_enabled:
        amqp_protocol = "amqps"
    if port:
        host_url = host + ":" + str(port)
    credentials = f"{username}:{password}@" if username and password else ""
    params = pika.URLParameters(f"{amqp_protocol}://{credentials}{host_url}/{virtual_host}")
    return BlockingConnection(params)


def consume_messages():
    # Establish a new connection and channel for each thread
    connection = pika.BlockingConnection(pika.ConnectionParameters('172.17.0.1')) ##TODO: Have to update the host later
    channel = connection.channel()
    
    # Ensure the queue exists
    # channel.queue_declare(queue=queue_name, durable=True)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange='direct_logs', queue=queue_name, routing_key="info")
    
    # Set up a consumer
    for method_frame, properties, body in channel.consume(queue=queue_name, auto_ack=False, inactivity_timeout=60):
        if method_frame:
            print(f" [x] Received {body.decode()}")
            try:
                response = requests.post(URL, json=body.decode())
                print(response)
                print(" [x] Done")
            except Exception as e:
                print("Exception occured in sending response to API")

            # Acknowledge the message
            channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        else:
            # Inactivity timeout reached, check if the thread should stop
            print("Stopping the Message Consumer for this Invocation of Write function")
            # Implement your logic here to decide whether to break the loop
            # For example, you can check a condition or wait for a signal
            break
    
    # Cancel the consumer and close the connection when done
    channel.cancel()
    connection.close()


def start_consumer_thread():
    print("Consumer Thread started")
    consumer_thread = threading.Thread(target=consume_messages)
    consumer_thread.start()
    return consumer_thread


class DestinationLamatic(Destination):
    def write(
        self, config: Mapping[str, Any], configured_catalog: ConfiguredAirbyteCatalog, input_messages: Iterable[AirbyteMessage]
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
        print("Executing this function")
        consumer_thread = start_consumer_thread()
        time.sleep(1)
        
        exchange = config.get("exchange")
        routing_key = config["routing_key"]
        # for message in input_messages:
        #     print(message)
        
        # time.sleep(5)

        connection = create_connection(config=config)
        channel = connection.channel()

        streams = {s.stream.name for s in configured_catalog.streams}
        try:
            for message in input_messages:
                if message.type == Type.STATE:
                    # Emitting a state message means all records that came before it
                    # have already been published.
                    yield message
                elif message.type == Type.RECORD:
                    record = message.record
                    if record.stream not in streams:
                        # Message contains record from a stream that is not in the catalog. Skip it!
                        continue
                    print(message)
                    headers = {"stream": record.stream, "emitted_at": record.emitted_at, "namespace": record.namespace}
                    properties = BasicProperties(content_type="application/json", headers=headers)
                    channel.basic_publish(
                        exchange=exchange or "", routing_key=routing_key, properties=properties, body=json.dumps(record.data)
                    )
                else:
                    # Let's ignore other message types for now
                    continue
            consumer_thread.join()
        finally:
            connection.close()

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
            # TODO

            return AirbyteConnectionStatus(status=Status.SUCCEEDED)
        except Exception as e:
            return AirbyteConnectionStatus(status=Status.FAILED, message=f"An exception occurred: {repr(e)}")
