package io.airbyte.cdk.output

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.discover.Field
import io.airbyte.cdk.output.sockets.SocketJsonOutputConsumer
import io.airbyte.cdk.output.sockets.InternalRow
import io.airbyte.cdk.output.sockets.SocketProtobufOutputConsumer
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.FieldValueChange
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.SocketResource
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import io.micronaut.context.annotation.Prototype
import jakarta.inject.Inject
import java.time.Clock

/**
 * OutputMessageRouter is responsible for building the appropriate routes for messages output.
 * Record message stream state and status traces may go over std output, or over sockets in JSONL or Protobuf format.
 * All other message like log or error messages go over std output.
 */
class OutputMessageRouter(
    private val recordsDataChannelMedium: DataChannelMedium,
    private val recordsDataChannelFormat: DataChannelFormat,
    private val simpleOutputConsumer: SimpleOutputConsumer,
    private val additionalProperties: Map<String, String>,
    private val feedBootstrap: FeedBootstrap<*>,
    private val acquiredResources: Map<ResourceType, Resource.Acquired>, )
    : AutoCloseable {

    enum class DataChannelFormat {
        JSONL,
        PROTOBUF,
    }

    enum class DataChannelMedium {
        STDIO,
        SOCKET,
    }

    private lateinit var socketJsonOutputConsumer: SocketJsonOutputConsumer
    private lateinit var efficientStreamRecordConsumers: Map<StreamIdentifier, StreamRecordConsumer>
    private lateinit var protoOutputConsumer: SocketProtobufOutputConsumer
    private lateinit var protoRecordOutputConsumers: Map<StreamIdentifier, FeedBootstrap<*>.ProtoEfficientStreamRecordConsumer>
    private lateinit var simpleEfficientStreamConsumers: Map<StreamIdentifier, StreamRecordConsumer>
    var recordAcceptors: Map<StreamIdentifier, (InternalRow, Map<Field, FieldValueChange>?) -> Unit>

    init {
        when (recordsDataChannelMedium) {
            DataChannelMedium.SOCKET -> {
                when (recordsDataChannelFormat) {
                    DataChannelFormat.JSONL -> {
                        socketJsonOutputConsumer = SocketJsonOutputConsumer(
                            (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET] as SocketResource.AcquiredSocket).socketWrapper,
                            Clock.systemUTC(),  // TEMP
                            8192, // TEMP
                            additionalProperties
                        )
                        efficientStreamRecordConsumers =
                            feedBootstrap.streamRecordConsumers(socketJsonOutputConsumer)
                        recordAcceptors = efficientStreamRecordConsumers.map {
                            it.key to { record: InternalRow, changes: Map<Field, FieldValueChange>? -> it.value.accept(record, changes) }
                        }
                            .toMap()
                    }

                    DataChannelFormat.PROTOBUF -> {
                        protoOutputConsumer = SocketProtobufOutputConsumer(
                            (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET] as SocketResource.AcquiredSocket).socketWrapper,
                            Clock.systemUTC(),
                            8192
                        )
                        protoRecordOutputConsumers = feedBootstrap.streamProtoRecordConsumers(
                            protoOutputConsumer,
                            additionalProperties["partition_id"]
                        )
                        recordAcceptors = protoRecordOutputConsumers.map {
                            it.key to { record: InternalRow, changes: Map<Field, FieldValueChange>? -> it.value.accept(record, changes) }
                        }
                            .toMap()
                    }
                }
            }
            DataChannelMedium.STDIO -> {
                simpleEfficientStreamConsumers = feedBootstrap.streamRecordConsumers()
                recordAcceptors = simpleEfficientStreamConsumers.map {
                    it.key to { record: InternalRow, changes: Map<Field, FieldValueChange>? -> it.value.accept(record, changes) }
                }
                    .toMap()
            }
        }
    }

    override fun close() {
        if (::simpleEfficientStreamConsumers.isInitialized) {
            simpleEfficientStreamConsumers.forEach { it.value.close() }
        }
        if (::protoRecordOutputConsumers.isInitialized) {
            protoRecordOutputConsumers.forEach { it.value.close() }
        }
        if (::efficientStreamRecordConsumers.isInitialized) {
            efficientStreamRecordConsumers.forEach { it.value.close() }
        }
    }

    fun acceptNonRecord(airbyteMessage: AirbyteStateMessage) {
        when (recordsDataChannelMedium) {
            DataChannelMedium.SOCKET -> {
                when (recordsDataChannelFormat) {
                    DataChannelFormat.JSONL -> socketJsonOutputConsumer.accept(airbyteMessage)
                    DataChannelFormat.PROTOBUF -> protoOutputConsumer.accept(airbyteMessage)
                    /*        if (needAlsoSimpleOutout && recordsDataChannelFormat != DataChannelFormat.STDIO) {
                                simpleOutputConsumer.accept(airbyteMessage)
                            }*/

                }
            }
            DataChannelMedium.STDIO -> {
                simpleOutputConsumer.accept(airbyteMessage)
            }
        }

    }

    fun acceptNonRecord(airbyteMessage: AirbyteStreamStatusTraceMessage) {
        when (recordsDataChannelMedium) {
            DataChannelMedium.SOCKET -> {
                when (recordsDataChannelFormat) {
                    DataChannelFormat.JSONL -> socketJsonOutputConsumer.accept(airbyteMessage)
                    DataChannelFormat.PROTOBUF -> protoOutputConsumer.accept(airbyteMessage)
                    /*        if (needAlsoSimpleOutout && recordsDataChannelFormat != DataChannelFormat.STDIO) {
                                simpleOutputConsumer.accept(airbyteMessage)
                            }*/

                }
            }
            DataChannelMedium.STDIO -> {
                simpleOutputConsumer.accept(airbyteMessage)
            }
        }
    }

}
