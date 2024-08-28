# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

from airbyte_cdk.models import AirbyteMessage, Type
from airbyte_cdk.sources.connector_state_manager import HashableStreamDescriptor
from airbyte_protocol_dataclasses.models import *


def get_stream_descriptor(message: AirbyteMessage) -> HashableStreamDescriptor:
    mtype = message.type  # Cache the access to message.type
    if mtype == Type.RECORD:
        record = message.record  # Cache the access to message.record
        return HashableStreamDescriptor(name=record.stream, namespace=record.namespace)
    elif mtype == Type.STATE:
        state = message.state  # Cache the access to message.state
        stream = state.stream  # Cache the access to state.stream
        descriptor = stream.stream_descriptor  # Cache the access to stream.stream_descriptor
        if not stream or not descriptor:
            raise ValueError("State message was not in per-stream state format, which is required for record counts.")
        return HashableStreamDescriptor(name=descriptor.name, namespace=descriptor.namespace)
    else:
        raise NotImplementedError(f"get_stream_descriptor is not implemented for message type '{mtype}'.")
