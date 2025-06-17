package io.airbyte.cdk.output

import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.output.sockets.SocketJsonOutputConsumer
import io.airbyte.cdk.output.sockets.InternalRow
import io.airbyte.cdk.output.sockets.SocketProtobufOutputConsumer
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.SocketResource
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import java.time.Clock

/**
 * OutputMessageRouter is responsible for building the appropriate routes for messages output.
 * Record message stream state and status traces may go over std output, or over sockets in JSONL or Protobuf format.
 * All other message like log or error messages go over std output.
 */
class OutputMessageRouter(
    private val recordsChannelType: OutputChannelType,
    private val simpleOutputConsumer: SimpleOutputConsumer,
    private val additionalProperties: Map<String, String>,
    private val feedBootstrap: FeedBootstrap<*>,
    private val acquiredResources: Map<ResourceType, Resource.Acquired>, )
    : AutoCloseable {

    enum class OutputChannelType {
        JSONL,
        PROTOBUF,
        STDIO
    }

    private lateinit var socketJsonOutputConsumer: SocketJsonOutputConsumer
    private lateinit var efficientStreamRecordConsumers: Map<StreamIdentifier, StreamRecordConsumer>
    private lateinit var protoOutputConsumer: SocketProtobufOutputConsumer
    private lateinit var protoRecordOutputConsumers: Map<StreamIdentifier, FeedBootstrap<*>.ProtoEfficientStreamRecordConsumer>
    private lateinit var simpleEfficientStreamConsumers: Map<StreamIdentifier, StreamRecordConsumer>
    lateinit var recordAcceptors: Map<StreamIdentifier, (InternalRow) -> Unit>

    init {

        when (recordsChannelType) {
            OutputChannelType.JSONL -> {
                socketJsonOutputConsumer = SocketJsonOutputConsumer(
                    (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET] as SocketResource.AcquiredSocket).socketWrapper,
                    Clock.systemUTC(),
                    8192,
                    additionalProperties
                )
                efficientStreamRecordConsumers = feedBootstrap.streamRecordConsumers(socketJsonOutputConsumer)
                recordAcceptors = efficientStreamRecordConsumers.map {
                    it.key to { record: InternalRow -> it.value.accept(record, emptyMap()) } }
                    .toMap()

            }
            OutputChannelType.PROTOBUF -> {
                protoOutputConsumer = SocketProtobufOutputConsumer(
                    (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET] as SocketResource.AcquiredSocket).socketWrapper,
                    Clock.systemUTC(),
                    8192
                )
                protoRecordOutputConsumers = feedBootstrap.streamProtoRecordConsumers(protoOutputConsumer, additionalProperties["partition_id"])
                recordAcceptors = protoRecordOutputConsumers.map {
                    it.key to { record: InternalRow -> it.value.accept(record, emptyMap()) } }
                    .toMap()
            }
            OutputChannelType.STDIO -> {
                simpleEfficientStreamConsumers = feedBootstrap.streamRecordConsumers()

                // TODO: add acceptors?
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

    fun acceptRecord(record: InternalRow, streamIdentifier: StreamIdentifier) {
        when (recordsChannelType) {
            OutputChannelType.JSONL -> efficientStreamRecordConsumers[streamIdentifier]?.accept(record, emptyMap()) // TEMP
            OutputChannelType.PROTOBUF -> protoRecordOutputConsumers[streamIdentifier]?.accept(record, emptyMap())
            OutputChannelType.STDIO -> simpleEfficientStreamConsumers[streamIdentifier]?.accept(record, emptyMap())
        }

    }

    fun acceptNonRecord(airbyteMessage: AirbyteStateMessage, needAlsoSimpleOutout: Boolean) {
        when (recordsChannelType) {
            OutputChannelType.JSONL -> socketJsonOutputConsumer.accept(airbyteMessage)
            OutputChannelType.PROTOBUF -> protoOutputConsumer.accept(airbyteMessage)
            OutputChannelType.STDIO -> simpleOutputConsumer.accept(airbyteMessage)
        }

        if (needAlsoSimpleOutout && recordsChannelType != OutputChannelType.STDIO) {
            simpleOutputConsumer.accept(airbyteMessage)
        }
    }

    fun acceptNonRecord(airbyteMessage: AirbyteStreamStatusTraceMessage, needAlsoSimpleOutout: Boolean) {
        when (recordsChannelType) {
            OutputChannelType.JSONL -> socketJsonOutputConsumer.accept(airbyteMessage)
            OutputChannelType.PROTOBUF -> protoOutputConsumer.accept(airbyteMessage)
            OutputChannelType.STDIO -> simpleOutputConsumer.accept(airbyteMessage)
        }

        if (needAlsoSimpleOutout && recordsChannelType != OutputChannelType.STDIO) {
            simpleOutputConsumer.accept(airbyteMessage)
        }
    }

}
