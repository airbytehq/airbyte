/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.output

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.sockets.NativeRecordPayload
import io.airbyte.cdk.output.sockets.SocketJsonOutputConsumer
import io.airbyte.cdk.output.sockets.SocketProtobufOutputConsumer
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.SocketResource
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage

/**
 * OutputMessageRouter is responsible for building the appropriate routes for messages output.
 * Record message stream state and status traces may go over std output, or over sockets in JSONL or
 * Protobuf format. All other message like log or error messages go over std output.
 */
class OutputMessageRouter(
    private val recordsDataChannelMedium: DataChannelMedium,
    private val recordsDataChannelFormat: DataChannelFormat,
    private val standardOutputConsumer: StandardOutputConsumer,
    additionalProperties: Map<String, String>,
    feedBootstrap: FeedBootstrap<*>,
    acquiredResources: Map<ResourceType, Resource.Acquired>,
) : AutoCloseable {
    private lateinit var socketJsonOutputConsumer: SocketJsonOutputConsumer
    private lateinit var socketJsonStreamRecordConsumers:
        Map<StreamIdentifier, StreamRecordConsumer>
    private lateinit var socketProtobufOutputConsumer: SocketProtobufOutputConsumer
    private lateinit var protoStreamRecordOutputConsumers:
        Map<StreamIdentifier, FeedBootstrap<*>.ProtoEfficientStreamRecordConsumer>
    private lateinit var simpleEfficientStreamConsumers: Map<StreamIdentifier, StreamRecordConsumer>
    var recordAcceptors:
        Map<StreamIdentifier, (NativeRecordPayload, Map<Field, FieldValueChange>?) -> Unit>

    init {
        when (recordsDataChannelMedium) {
            DataChannelMedium.SOCKET -> {
                when (recordsDataChannelFormat) {
                    DataChannelFormat.JSONL -> {
                        socketJsonOutputConsumer =
                            SocketJsonOutputConsumer(
                                (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET]
                                        as SocketResource.AcquiredSocket)
                                    .socketDatachannel,
                                feedBootstrap.clock,
                                feedBootstrap.bufferByteSizeThresholdForFlush,
                                additionalProperties
                            )
                        socketJsonStreamRecordConsumers =
                            feedBootstrap.streamJsonSocketRecordConsumers(socketJsonOutputConsumer)
                        recordAcceptors =
                            socketJsonStreamRecordConsumers
                                .map {
                                    it.key to
                                        {
                                            record: NativeRecordPayload,
                                            changes: Map<Field, FieldValueChange>? ->
                                            it.value.accept(record, changes)
                                        }
                                }
                                .toMap()
                    }
                    DataChannelFormat.PROTOBUF -> {
                        socketProtobufOutputConsumer =
                            SocketProtobufOutputConsumer(
                                (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET]
                                        as SocketResource.AcquiredSocket)
                                    .socketDatachannel,
                                feedBootstrap.clock,
                                feedBootstrap.bufferByteSizeThresholdForFlush,
                                additionalProperties
                            )
                        protoStreamRecordOutputConsumers =
                            feedBootstrap.streamProtoRecordConsumers(
                                socketProtobufOutputConsumer,
                            )
                        recordAcceptors =
                            protoStreamRecordOutputConsumers
                                .map {
                                    it.key to
                                        {
                                            record: NativeRecordPayload,
                                            changes: Map<Field, FieldValueChange>? ->
                                            it.value.accept(record, changes)
                                        }
                                }
                                .toMap()
                    }
                }
            }
            DataChannelMedium.STDIO -> {
                simpleEfficientStreamConsumers = feedBootstrap.streamRecordConsumers()
                recordAcceptors =
                    simpleEfficientStreamConsumers
                        .map {
                            it.key to
                                {
                                    record: NativeRecordPayload,
                                    changes: Map<Field, FieldValueChange>? ->
                                    it.value.accept(record, changes)
                                }
                        }
                        .toMap()
            }
        }
    }

    fun acceptNonRecord(airbyteMessage: AirbyteStateMessage) {
        when (recordsDataChannelMedium) {
            DataChannelMedium.SOCKET -> {
                when (recordsDataChannelFormat) {
                    DataChannelFormat.JSONL -> socketJsonOutputConsumer.accept(airbyteMessage)
                    DataChannelFormat.PROTOBUF ->
                        socketProtobufOutputConsumer.accept(airbyteMessage)
                }
            }
            DataChannelMedium.STDIO -> {
                standardOutputConsumer.accept(airbyteMessage)
            }
        }
    }

    fun acceptNonRecord(airbyteMessage: AirbyteStreamStatusTraceMessage) {
        when (recordsDataChannelMedium) {
            DataChannelMedium.SOCKET -> {
                when (recordsDataChannelFormat) {
                    DataChannelFormat.JSONL -> socketJsonOutputConsumer.accept(airbyteMessage)
                    DataChannelFormat.PROTOBUF ->
                        socketProtobufOutputConsumer.accept(airbyteMessage)
                }
            }
            DataChannelMedium.STDIO -> {
                standardOutputConsumer.accept(airbyteMessage)
            }
        }
    }

    @SuppressFBWarnings(value = ["RCN_REDUNDANT_NULLCHECK_OF_NONNULL_VALUE"])
    override fun close() {
        if (::simpleEfficientStreamConsumers.isInitialized) {
            simpleEfficientStreamConsumers.forEach { it.value.close() }
        }
        if (::protoStreamRecordOutputConsumers.isInitialized) {
            protoStreamRecordOutputConsumers.forEach { it.value.close() }
        }
        if (::socketJsonStreamRecordConsumers.isInitialized) {
            socketJsonStreamRecordConsumers.forEach { it.value.close() }
        }
    }
}
