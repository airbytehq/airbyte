package io.airbyte.cdk.core.destination.async

import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import com.google.common.base.Strings
import io.airbyte.cdk.core.config.AirbyteConfiguredCatalog
import io.airbyte.cdk.core.config.ConnectorConfiguration
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.core.destination.async.buffer.BufferEnqueue
import io.airbyte.cdk.core.destination.async.function.OnCloseFunction
import io.airbyte.cdk.core.destination.async.function.OnStartFunction
import io.airbyte.cdk.core.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import java.util.Optional
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.atomic.AtomicLong
import java.util.stream.Collectors

private val logger = KotlinLogging.logger {}

@Singleton
@Requires(
    property = ConnectorConfigurationPropertySource.CONNECTOR_OPERATION,
    value = "write",
)
@Requires(env = ["destination"])
class AsyncStreamConsumer(
    private val onStart: OnStartFunction,
    private val onClose: OnCloseFunction,
    private val connectorConfiguration: ConnectorConfiguration,
    private val airbyteConfiguredCatalog: AirbyteConfiguredCatalog,
    private val bufferEnqueue: BufferEnqueue,
    private val flushWorkers: FlushWorkers,
    private val flushFailure: FlushFailure,
    private val streamDescriptorUtils: StreamDescriptorUtils,
) : SerializedAirbyteMessageConsumer {
    private var hasClosed = false
    private var hasFailed = false
    private var hasStarted = false
    private val recordCounts: ConcurrentMap<StreamDescriptor, AtomicLong> = ConcurrentHashMap()
    private val streamNames: Set<StreamDescriptor> =
        streamDescriptorUtils.fromConfiguredCatalog(airbyteConfiguredCatalog.getConfiguredCatalog())

    companion object {
        // This is to account for the references when deserialization to a PartialAirbyteMessage. The
        // calculation is as follows:
        // PartialAirbyteMessage (4) + Max( PartialRecordMessage(4), PartialStateMessage(6)) with
        // PartialStateMessage being larger with more nested objects within it. Using 8 bytes as we assumed
        // a 64 bit JVM.
        const val PARTIAL_DESERIALIZE_REF_BYTES: Int = 10 * 8
    }

    override fun accept(
        message: String,
        sizeInBytes: Int,
    ) {
        Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started")
        propagateFlushWorkerExceptionIfPresent()

        /*
         * intentionally putting extractStream outside the buffer manager so that if in the future we want
         * to try to use a thread pool to partially deserialize to get record type and stream name, we can
         * do it without touching buffer manager.
         */
        val airbyteMessage = deserializeAirbyteMessage(message)
        if (AirbyteMessage.Type.RECORD == airbyteMessage.type) {
            if (Strings.isNullOrEmpty(airbyteMessage.record?.namespace)) {
                airbyteMessage.record!!.namespace = connectorConfiguration.getDefaultNamespace().orElse(null)
            }
            validateRecord(airbyteMessage)

            airbyteMessage.record?.let { getRecordCounter(it.getStreamDescriptor()).incrementAndGet() }
        }
        bufferEnqueue.addRecord(
            airbyteMessage,
            sizeInBytes + PARTIAL_DESERIALIZE_REF_BYTES,
            connectorConfiguration.getDefaultNamespace().orElse(""),
        )
    }

    override fun close() {
        Preconditions.checkState(hasStarted, "Cannot close; has not started.")
        Preconditions.checkState(!hasClosed, "Has already closed.")
        hasClosed = true

        // assume closing upload workers will flush all accepted records.
        // we need to close the workers before closing the bufferManagers (and underlying buffers)
        // or we risk in-memory data.
        flushWorkers.close()

        val streamSyncSummaries =
            streamNames.stream().collect(
                Collectors.toMap(
                    { streamDescriptor: StreamDescriptor -> streamDescriptor },
                    { streamDescriptor: StreamDescriptor ->
                        StreamSyncSummary(
                            Optional.of(getRecordCounter(streamDescriptor).get()),
                        )
                    },
                ),
            )
        onClose.accept(hasFailed, streamSyncSummaries)

        // as this throws an exception, we need to be after all the other close functions.
        propagateFlushWorkerExceptionIfPresent()
        logger.info { "${AsyncStreamConsumer::class.java.name} closed" }
    }

    override fun start() {
        Preconditions.checkState(!hasStarted, "Consumer has already been started.")
        hasStarted = true

        flushWorkers.start()

        logger.info { "${AsyncStreamConsumer::class.java.name} started." }
        onStart.call()
    }

    /**
     * Deserializes to a [PartialAirbyteMessage] which can represent both a Record or a State
     * Message
     *
     * PartialAirbyteMessage holds either:
     *  * entire serialized message string when message is a valid State Message
     *  * serialized AirbyteRecordMessage when message is a valid Record Message
     *
     * @param messageString the string to deserialize
     * @return PartialAirbyteMessage if the message is valid, empty otherwise
     */
    @VisibleForTesting
    fun deserializeAirbyteMessage(messageString: String): PartialAirbyteMessage {
        // TODO: (ryankfu) plumb in the serialized AirbyteStateMessage to match AirbyteRecordMessage code
        // parity. https://github.com/airbytehq/airbyte/issues/27530 for additional context
        val partial = Jsons.tryDeserializeExact(messageString, PartialAirbyteMessage::class.java)
            .orElseThrow { RuntimeException("Unable to deserialize PartialAirbyteMessage.") }

        val msgType = partial.type
        if (AirbyteMessage.Type.RECORD == msgType && partial.record?.data != null) {
            // store serialized json
            partial.withSerialized(partial.record?.data.toString())
            // The connector doesn't need to be able to access to the record value. We can serialize it here and
            // drop the json
            // object. Having this data stored as a string is slightly more optimal for the memory usage.
            partial.record?.data = null
        } else if (AirbyteMessage.Type.STATE == msgType) {
            partial.withSerialized(messageString)
        } else {
            throw RuntimeException(String.format("Unsupported message type: %s", msgType))
        }

        return partial
    }

    private fun getRecordCounter(streamDescriptor: StreamDescriptor): AtomicLong {
        return recordCounts.computeIfAbsent(streamDescriptor) { AtomicLong() }
    }

    @Throws(Exception::class)
    private fun propagateFlushWorkerExceptionIfPresent() {
        if (flushFailure.isFailed()) {
            hasFailed = true
            throw flushFailure.getException()
        }
    }

    private fun validateRecord(message: PartialAirbyteMessage) {
        val streamDescriptor =
            StreamDescriptor()
                .withNamespace(message.record?.namespace)
                .withName(message.record?.stream)
        // if stream is not part of list of streams to sync to then throw invalid stream exception
        if (!streamNames.contains(streamDescriptor)) {
            throwUnrecognizedStream(airbyteConfiguredCatalog.getConfiguredCatalog(), message)
        }
    }

    private fun throwUnrecognizedStream(
        catalog: ConfiguredAirbyteCatalog,
        message: PartialAirbyteMessage,
    ) {
        throw IllegalArgumentException(
            "Message contained record from a stream that was not in the catalog. \ncatalog: ${Jsons.serialize(
                catalog,
            )} , \nmessage: ${Jsons.serialize(message)}",
        )
    }
}
