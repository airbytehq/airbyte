package io.airbyte.cdk.output

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
 * OutputMessageRouter is responsible for building the appropriate routes for messages output
 */
class OutputMessageRouter(
    private val recordsChannelType: OutputChannelType,
    private val simpleOutputConsumer: SimpleOutputConsumer,
    private val additionalProperties: Map<String, String>,
    private val streamFeedBootstrap: StreamFeedBootstrap,
    private val acquiredResources: Map<ResourceType, Resource.Acquired>, )
    : AutoCloseable {

    enum class OutputChannelType {
        JSONL,
        PROTOBUF,
        STDIO
    }

    private lateinit var socketJsonOutputConsumer: SocketJsonOutputConsumer
    private lateinit var efficientStreamRecordConsumer: StreamRecordConsumer
    private lateinit var protoOutputConsumer: SocketProtobufOutputConsumer
    private lateinit var protoRecordOutputConsumer: FeedBootstrap<*>.ProtoEfficientStreamRecordConsumer
    private lateinit var simpleEfficientStreamConsumer: StreamRecordConsumer
    lateinit var recordAcceptor: (InternalRow) -> Unit

    init {

        when (recordsChannelType) {
            OutputChannelType.JSONL -> {
                socketJsonOutputConsumer = SocketJsonOutputConsumer(
                    (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET] as SocketResource.AcquiredSocket).socketWrapper,
                    Clock.systemUTC(),
                    8192,
                    additionalProperties
                )
                efficientStreamRecordConsumer = streamFeedBootstrap.streamRecordConsumer(socketJsonOutputConsumer)
                recordAcceptor = { record ->
                    efficientStreamRecordConsumer.accept(record, emptyMap())
                }
            }
            OutputChannelType.PROTOBUF -> {
                protoOutputConsumer = SocketProtobufOutputConsumer(
                    (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET] as SocketResource.AcquiredSocket).socketWrapper,
                    Clock.systemUTC(),
                    8192
                )
                protoRecordOutputConsumer = streamFeedBootstrap.protoStreamRecordConsumer(protoOutputConsumer, additionalProperties["partition_id"])
                recordAcceptor = { record ->
                    protoRecordOutputConsumer.accept(record, emptyMap())
                }
            }
            OutputChannelType.STDIO -> {
                simpleEfficientStreamConsumer = streamFeedBootstrap.streamRecordConsumer(null)
            }
            }
        }

    override fun close() {
/*
        if (::boostedOutputConsumer.isInitialized) {
            boostedOutputConsumer.close()
        }
    if (::protoOutputConsumer.isInitialized) {
                protoOutputConsumer.close()
    }
*/
        if (::simpleEfficientStreamConsumer.isInitialized) {
            simpleEfficientStreamConsumer.close()
        }
        if (::protoRecordOutputConsumer.isInitialized) {
            protoRecordOutputConsumer.close()
        }
    if (::efficientStreamRecordConsumer.isInitialized) {
                efficientStreamRecordConsumer.close()
            }

    }

    fun acceptRecord(record: InternalRow) {
        when (recordsChannelType) {
            OutputChannelType.JSONL -> efficientStreamRecordConsumer.accept(record, emptyMap())
            OutputChannelType.PROTOBUF -> protoRecordOutputConsumer.accept(record, emptyMap())
            OutputChannelType.STDIO -> simpleEfficientStreamConsumer.accept(record, emptyMap())
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
