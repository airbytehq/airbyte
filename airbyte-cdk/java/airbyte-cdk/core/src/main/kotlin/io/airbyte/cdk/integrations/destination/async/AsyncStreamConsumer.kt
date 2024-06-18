/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import com.google.common.base.Preconditions
import io.airbyte.cdk.integrations.base.SerializedAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.StreamSyncSummary
import io.airbyte.cdk.integrations.destination.async.buffers.BufferEnqueue
import io.airbyte.cdk.integrations.destination.async.buffers.BufferManager
import io.airbyte.cdk.integrations.destination.async.deser.AirbyteMessageDeserializer
import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction
import io.airbyte.cdk.integrations.destination.async.model.PartialAirbyteMessage
import io.airbyte.cdk.integrations.destination.async.state.FlushFailure
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnCloseFunction
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.OnStartFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamStatusTraceMessage.AirbyteStreamStatus
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.concurrent.ConcurrentHashMap
import java.util.concurrent.ConcurrentMap
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.atomic.AtomicLong
import java.util.function.Consumer
import org.jetbrains.annotations.VisibleForTesting

private val logger = KotlinLogging.logger {}

/**
 * Async version of the
 * [io.airbyte.cdk.integrations.destination.buffered_stream_consumer.BufferedStreamConsumer].
 *
 * With this consumer, a destination is able to continue reading records until hitting the maximum
 * memory limit governed by [GlobalMemoryManager]. Record writing is decoupled via [FlushWorkers].
 * See the other linked class for more detail.
 */
open class AsyncStreamConsumer
@VisibleForTesting
@JvmOverloads
constructor(
    outputRecordCollector: Consumer<AirbyteMessage>,
    private val onStart: OnStartFunction,
    private val onClose: OnCloseFunction,
    onFlush: DestinationFlushFunction,
    private val catalog: ConfiguredAirbyteCatalog,
    private val bufferManager: BufferManager,
    private val flushFailure: FlushFailure = FlushFailure(),
    workerPool: ExecutorService = Executors.newFixedThreadPool(5),
    private val airbyteMessageDeserializer: AirbyteMessageDeserializer =
        AirbyteMessageDeserializer(),
) : SerializedAirbyteMessageConsumer {
    private val bufferEnqueue: BufferEnqueue = bufferManager.bufferEnqueue
    private val flushWorkers: FlushWorkers =
        FlushWorkers(
            bufferManager.bufferDequeue,
            onFlush,
            outputRecordCollector,
            flushFailure,
            bufferManager.stateManager,
            workerPool,
        )
    private val streamNames: Set<StreamDescriptor> =
        StreamDescriptorUtils.fromConfiguredCatalog(
            catalog,
        )

    // Note that this map will only be populated for streams with nonzero records.
    private val recordCounts: ConcurrentMap<StreamDescriptor, AtomicLong> = ConcurrentHashMap()
    private val terminalStatusesFromSource: ConcurrentMap<StreamDescriptor, AirbyteStreamStatus> =
        ConcurrentHashMap()

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
        val partialAirbyteMessage =
            airbyteMessageDeserializer.deserializeAirbyteMessage(
                message,
            )
        when (partialAirbyteMessage.type) {
            AirbyteMessage.Type.RECORD -> {
                validateRecord(partialAirbyteMessage)

                partialAirbyteMessage.record?.streamDescriptor?.let {
                    getRecordCounter(it).incrementAndGet()

                    if (terminalStatusesFromSource.containsKey(it)) {
                        throw IllegalStateException(
                            "Received a record message after a terminal stream status for stream ${it.namespace}.${it.name}"
                        )
                    }
                }
            }
            AirbyteMessage.Type.TRACE -> {
                // There are many types of trace messages, but we only care about stream status
                // messages with status=COMPLETE or INCOMPLETE.
                // INCOMPLETE is a slightly misleading name - it actually means "Stream has stopped
                // due to an interruption or error", i.e. failure
                partialAirbyteMessage.trace?.streamStatus?.let {
                    val isTerminalStatus =
                        it.status == AirbyteStreamStatus.COMPLETE ||
                            it.status == AirbyteStreamStatus.INCOMPLETE
                    if (isTerminalStatus) {
                        val conflictsWithExistingStatus =
                            terminalStatusesFromSource.containsKey(it.streamDescriptor) &&
                                terminalStatusesFromSource[it.streamDescriptor] != it.status
                        if (conflictsWithExistingStatus) {
                            throw IllegalStateException(
                                "Received conflicting stream statuses for stream ${it.streamDescriptor.namespace}.${it.streamDescriptor.name}"
                            )
                        }
                        terminalStatusesFromSource[it.streamDescriptor] = it.status
                    }
                }
            }
            else -> {}
        }
        bufferEnqueue.addRecord(
            partialAirbyteMessage,
            sizeInBytes + PARTIAL_DESERIALIZE_REF_BYTES,
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

        val unsuccessfulStreams = ArrayList<StreamDescriptor>()
        val streamSyncSummaries =
            streamNames.associate { streamDescriptor ->
                // If we didn't receive a stream status message, assume failure.
                // This is possible if e.g. the orchestrator crashes before sending us the message.
                val terminalStatusFromSource =
                    terminalStatusesFromSource[streamDescriptor] ?: AirbyteStreamStatus.INCOMPLETE
                if (terminalStatusFromSource == AirbyteStreamStatus.INCOMPLETE) {
                    unsuccessfulStreams.add(streamDescriptor)
                }
                StreamDescriptorUtils.withDefaultNamespace(
                    streamDescriptor,
                    bufferManager.defaultNamespace,
                ) to
                    StreamSyncSummary(
                        getRecordCounter(streamDescriptor).get(),
                        terminalStatusFromSource,
                    )
            }
        onClose.accept(hasFailed, streamSyncSummaries)

        // as this throws an exception, we need to be after all other close functions.
        propagateFlushWorkerExceptionIfPresent()
        logger.info { "${AsyncStreamConsumer::class.java} closed" }

        // In principle, platform should detect this.
        // However, as a backstop, the destination should still do this check.
        // This handles e.g. platform bugs where we don't receive a stream status message.
        // In this case, it would be misleading to mark the sync as successful, because e.g. we
        // maybe didn't commit a truncate.
        if (unsuccessfulStreams.isNotEmpty()) {
            throw RuntimeException(
                "Some streams were unsuccessful due to a source error: $unsuccessfulStreams"
            )
        }
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
            throwUnrecognizedStream(catalog, message)
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
