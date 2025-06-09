package io.airbyte.cdk.output

import io.airbyte.cdk.output.sockets.BoostedOutputConsumer
import io.airbyte.cdk.output.sockets.InternalRow
import io.airbyte.cdk.output.sockets.ProtoRecordOutputConsumer
import io.airbyte.cdk.read.FeedBootstrap
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.SocketResource
import io.airbyte.cdk.read.StreamFeedBootstrap
import io.airbyte.cdk.read.StreamRecordConsumer
import io.airbyte.protocol.models.v0.AirbyteStateMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage
import java.time.Clock

class OutputMessageProcessor(
    private val outputType: OutputType,
    private val additionalProperties: Map<String, String>,
    private val streamFeedBootstrap: StreamFeedBootstrap,
    private val simpleOutputConsumer: OutputConsumer,
    private val acquiredResources: Map<ResourceType, Resource.Acquired>, )
    : AutoCloseable {

    enum class OutputType {
        JSON_SOCKET,
        PROTOBUF_SOCKET,
        SIMPLE_OUTPUT
    }

    private lateinit var boostedOutputConsumer: BoostedOutputConsumer
    private lateinit var efficientStreamRecordConsumer: StreamRecordConsumer
    private lateinit var protoOutputConsumer: ProtoRecordOutputConsumer
    private lateinit var protoRecordOutputConsumer: FeedBootstrap<*>.ProtoEfficientStreamRecordConsumer
    private lateinit var simpleEfficientStreamConsumer: StreamRecordConsumer
    lateinit var recordAcceptor: (InternalRow) -> Unit
    init {

    when (outputType) {
        OutputType.JSON_SOCKET -> {
            boostedOutputConsumer = BoostedOutputConsumer(
                (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET] as SocketResource.AcquiredSocket).socketWrapper,
                Clock.systemUTC(),
                8192,
                additionalProperties
            )
            efficientStreamRecordConsumer = streamFeedBootstrap.streamRecordConsumer(boostedOutputConsumer)
            recordAcceptor = { record ->
                efficientStreamRecordConsumer.accept(record, emptyMap())
            }
        }
        OutputType.PROTOBUF_SOCKET -> {
            protoOutputConsumer = ProtoRecordOutputConsumer(
                (acquiredResources[ResourceType.RESOURCE_OUTPUT_SOCKET] as SocketResource.AcquiredSocket).socketWrapper,
                Clock.systemUTC(),
                8192
            )
            protoRecordOutputConsumer = streamFeedBootstrap.protoStreamRecordConsumer(protoOutputConsumer, additionalProperties["partition_id"])
            recordAcceptor = { record ->
                protoRecordOutputConsumer.accept(record, emptyMap())
            }
        }
        OutputType.SIMPLE_OUTPUT -> {
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
        when (outputType) {
            OutputType.JSON_SOCKET -> efficientStreamRecordConsumer.accept(record, emptyMap())
            OutputType.PROTOBUF_SOCKET -> protoRecordOutputConsumer.accept(record, emptyMap())
            OutputType.SIMPLE_OUTPUT -> simpleEfficientStreamConsumer.accept(record, emptyMap())
        }

    }

    fun acceptNonRecord(airbyteMessage: AirbyteStateMessage, needAlsoSimpleOutout: Boolean) {
        when (outputType) {
            OutputType.JSON_SOCKET -> boostedOutputConsumer.accept(airbyteMessage)
            OutputType.PROTOBUF_SOCKET -> protoOutputConsumer.accept(airbyteMessage)
            OutputType.SIMPLE_OUTPUT -> simpleOutputConsumer.accept(airbyteMessage)
        }

        if (needAlsoSimpleOutout && outputType != OutputType.SIMPLE_OUTPUT) {
            simpleOutputConsumer.accept(airbyteMessage)
        }
    }

    fun acceptNonRecord(airbyteMessage: AirbyteStreamStatusTraceMessage, needAlsoSimpleOutout: Boolean) {
        when (outputType) {
            OutputType.JSON_SOCKET -> boostedOutputConsumer.accept(airbyteMessage)
            OutputType.PROTOBUF_SOCKET -> protoOutputConsumer.accept(airbyteMessage)
            OutputType.SIMPLE_OUTPUT -> simpleOutputConsumer.accept(airbyteMessage)
        }

        if (needAlsoSimpleOutout && outputType != OutputType.SIMPLE_OUTPUT) {
            simpleOutputConsumer.accept(airbyteMessage)
        }
    }

}
