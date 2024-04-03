/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import com.google.common.base.Strings
import io.airbyte.cdk.core.command.option.ConnectorConfiguration
import io.airbyte.cdk.core.command.option.MicronautConfiguredAirbyteCatalog
import io.airbyte.cdk.core.context.env.ConnectorConfigurationPropertySource
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.buffers.BufferEnqueue
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.DeserializationUtil
import io.airbyte.cdk.integrations.destination.async.deser.IdentityDataTransformer
import io.airbyte.cdk.integrations.destination.async.deser.StreamAwareDataTransformer
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
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
import kotlin.jvm.optionals.getOrNull

private val logger = KotlinLogging.logger {}

/**
 * Async version of the
 * [io.airbyte.cdk.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer].
 *
 * With this consumer, a destination is able to continue reading records until hitting the maximum
 * memory limit governed by [GlobalMemoryManager]. Record writing is decoupled via [FlushWorkers].
 * See the other linked class for more detail.
 */
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
    private val catalog: MicronautConfiguredAirbyteCatalog,
    private val bufferManager: BufferManager,
    private val flushWorkers: FlushWorkers,
    private val flushFailure: FlushFailure = FlushFailure(),
    private val dataTransformer: StreamAwareDataTransformer = IdentityDataTransformer(),
    private val deserializationUtil: DeserializationUtil = DeserializationUtil(),
) : SerializedAirbyteMessageConsumer {
    private val bufferEnqueue: BufferEnqueue = bufferManager.bufferEnqueue
    private val streamNames: Set<StreamDescriptor> =
        StreamDescriptorUtils.fromConfiguredCatalog(
            catalog.getConfiguredCatalog(),
        )

    // Note that this map will only be populated for streams with nonzero records.
    private val recordCounts: ConcurrentMap<StreamDescriptor, AtomicLong> = ConcurrentHashMap()

    private var hasStarted = false
    private var hasClosed = false
    private var hasFailed = false

    @Throws(Exception::class)
    override fun start() {
        Preconditions.checkState(!hasStarted, "Consumer has already been started.")
        hasStarted = true

        flushWorkers.start()

        logger.info { "${AsyncStreamConsumer::class.java} started." }
        onStart.call()
    }

    @Throws(Exception::class)
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
        val airbyteMessage =
            deserializationUtil.deserializeAirbyteMessage(
                message,
                dataTransformer,
            )
        if (AirbyteMessage.Type.RECORD == airbyteMessage.type) {
            if (Strings.isNullOrEmpty(airbyteMessage.record?.namespace)) {
                airbyteMessage.record?.namespace =
                    connectorConfiguration.getDefaultNamespace().getOrNull()
            }
            validateRecord(airbyteMessage)

            airbyteMessage.record?.streamDescriptor?.let { getRecordCounter(it).incrementAndGet() }
        }
        bufferEnqueue.addRecord(
            airbyteMessage,
            sizeInBytes + PARTIAL_DESERIALIZE_REF_BYTES,
            connectorConfiguration.getDefaultNamespace(),
        )
    }

    @Throws(Exception::class)
    override fun close() {
        Preconditions.checkState(hasStarted, "Cannot close; has not started.")
        Preconditions.checkState(!hasClosed, "Has already closed.")
        hasClosed = true

        // assume closing upload workers will flush all accepted records.
        // we need to close the workers before closing the bufferManagers (and underlying buffers)
        // or we risk in-memory data.
        flushWorkers.close()

        bufferManager.close()

        val streamSyncSummaries =
            streamNames
                .stream()
                .collect(
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
        logger.info { "${AsyncStreamConsumer::class.java} closed" }
    }

    private fun getRecordCounter(streamDescriptor: StreamDescriptor): AtomicLong {
        return recordCounts.computeIfAbsent(
            streamDescriptor,
        ) {
            AtomicLong()
        }
    }

    @Throws(Exception::class)
    private fun propagateFlushWorkerExceptionIfPresent() {
        if (flushFailure.isFailed()) {
            hasFailed = true
            throw flushFailure.exception
        }
    }

    private fun validateRecord(message: PartialAirbyteMessage) {
        val streamDescriptor =
            StreamDescriptor()
                .withNamespace(message.record?.namespace)
                .withName(message.record?.stream)
        // if stream is not part of list of streams to sync to then throw invalid stream exception
        if (!streamNames.contains(streamDescriptor)) {
            throwUnrecognizedStream(catalog.getConfiguredCatalog(), message)
        }
    }

    companion object {
        // This is to account for the references when deserialization to a PartialAirbyteMessage.
        // The calculation is as follows: PartialAirbyteMessage (4) + Max( PartialRecordMessage(4),
        // PartialStateMessage(6)) with PartialStateMessage being larger with more nested objects
        // within it. Using 8 bytes as we assumed a 64 bit JVM.
        private const val PARTIAL_DESERIALIZE_REF_BYTES: Int = 10 * 8

        private fun throwUnrecognizedStream(
            catalog: ConfiguredAirbyteCatalog?,
            message: PartialAirbyteMessage,
        ) {
            throw IllegalArgumentException(
                "Message contained record from a stream that was not in the catalog. " +
                    "\ncatalog: ${Jsons.serialize(catalog)}, " +
                    "\nmessage: ${Jsons.serialize(message)}",
            )
        }
    }
}
