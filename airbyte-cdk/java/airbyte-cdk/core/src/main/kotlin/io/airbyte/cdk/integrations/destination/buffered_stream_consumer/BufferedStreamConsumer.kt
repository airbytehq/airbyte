/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.buffered_stream_consumer

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import com.google.common.base.Strings
import io.airbyte.cdk.integrations.base.AirbyteMessageConsumer
import io.airbyte.cdk.integrations.base.FailureTrackingAirbyteMessageConsumer
import io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager.DefaultDestStateLifecycleManager
import io.airbyte.cdk.integrations.destination.dest_state_lifecycle_manager.DestStateLifecycleManager
import io.airbyte.cdk.integrations.destination.record_buffer.BufferFlushType
import io.airbyte.cdk.integrations.destination.record_buffer.BufferingStrategy
import io.airbyte.commons.functional.CheckedFunction
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.Instant
import java.util.function.Consumer

private val LOGGER = KotlinLogging.logger {}
/**
 * This class consumes AirbyteMessages from the worker.
 *
 * Record Messages: It adds record messages to a buffer. Under 2 conditions, it will flush the
 * records in the buffer to a temporary table in the destination. Condition 1: The buffer fills up
 * (the buffer is designed to be small enough as not to exceed the memory of the container).
 * Condition 2: On close.
 *
 * State Messages: This consumer tracks the last state message it has accepted. It also tracks the
 * last state message that was committed to the temporary table. For now, we only emit a message if
 * everything is successful. Once checkpointing is turned on, we will emit the state message as long
 * as the onClose successfully commits any messages to the raw table.
 *
 * All other message types are ignored.
 *
 * Throughout the lifecycle of the consumer, messages get promoted from buffered to flushed to
 * committed. A record message when it is received is immediately buffered. When the buffer fills
 * up, all buffered records are flushed out of memory using the user-provided recordBuffer. When
 * this flush happens, a state message is moved from pending to flushed. On close, if the
 * user-provided onClose function is successful, then the flushed state record is considered
 * committed and is then emitted. We expect this class to only ever emit either 1 state message (in
 * the case of a full or partial success) or 0 state messages (in the case where the onClose step
 * was never reached or did not complete without exception).
 *
 * When a record is "flushed" it is moved from the docker container to the destination. By
 * convention, it is usually placed in some sort of temporary storage on the destination (e.g. a
 * temporary database or file store). The logic in close handles committing the temporary
 * representation data to the final store (e.g. final table). In the case of staging destinations
 * they often have additional temporary stores. The common pattern for staging destination is that
 * flush pushes the data into a staging area in cloud storage and then close copies from staging to
 * a temporary table AND then copies from the temporary table into the final table. This abstraction
 * is blind to the detail of how staging destinations implement their close.
 */
class BufferedStreamConsumer
@VisibleForTesting
internal constructor(
    private val outputRecordCollector: Consumer<AirbyteMessage>,
    private val onStart: OnStartFunction,
    private val bufferingStrategy: BufferingStrategy,
    private val onClose: OnCloseFunction,
    private val catalog: ConfiguredAirbyteCatalog?,
    private val isValidRecord: CheckedFunction<JsonNode?, Boolean?, Exception?>,
    private val bufferFlushFrequency: Duration,
    private val defaultNamespace: String?
) : FailureTrackingAirbyteMessageConsumer(), AirbyteMessageConsumer {
    private val streamNames: Set<AirbyteStreamNameNamespacePair> =
        AirbyteStreamNameNamespacePair.fromConfiguredCatalog(catalog)
    private val streamToIgnoredRecordCount: MutableMap<AirbyteStreamNameNamespacePair, Long> =
        HashMap()
    private val stateManager: DestStateLifecycleManager =
        DefaultDestStateLifecycleManager(defaultNamespace)

    private var hasStarted = false
    private var hasClosed = false

    private var nextFlushDeadline: Instant? = null

    /**
     * Feel free to continue using this in non-1s1t destinations - it may be easier to use. However,
     * 1s1t destinations should prefer the version which accepts a `defaultNamespace`.
     */
    @Deprecated("")
    constructor(
        outputRecordCollector: Consumer<AirbyteMessage>,
        onStart: OnStartFunction,
        bufferingStrategy: BufferingStrategy,
        onClose: OnCloseFunction,
        catalog: ConfiguredAirbyteCatalog?,
        isValidRecord: CheckedFunction<JsonNode?, Boolean?, Exception?>
    ) : this(
        outputRecordCollector,
        onStart,
        bufferingStrategy,
        onClose,
        catalog,
        isValidRecord,
        Duration.ofMinutes(
            15
        ), // This is purely for backwards compatibility. Many older destinations handle this
        // internally.
        // Starting with Destinations V2, we recommend passing in an explicit namespace.
        null
    )

    constructor(
        outputRecordCollector: Consumer<AirbyteMessage>,
        onStart: OnStartFunction,
        bufferingStrategy: BufferingStrategy,
        onClose: OnCloseFunction,
        catalog: ConfiguredAirbyteCatalog?,
        isValidRecord: CheckedFunction<JsonNode?, Boolean?, Exception?>,
        defaultNamespace: String?
    ) : this(
        outputRecordCollector,
        onStart,
        bufferingStrategy,
        onClose,
        catalog,
        isValidRecord,
        Duration.ofMinutes(15),
        defaultNamespace
    )

    @Throws(Exception::class)
    override fun startTracked() {
        // todo (cgardens) - if we reuse this pattern, consider moving it into
        // FailureTrackingConsumer.
        Preconditions.checkState(!hasStarted, "Consumer has already been started.")
        hasStarted = true
        nextFlushDeadline = Instant.now().plus(bufferFlushFrequency)
        streamToIgnoredRecordCount.clear()
        LOGGER.info { "${BufferedStreamConsumer::class.java} started." }
        onStart.call()
    }

    /**
     * AcceptTracked will still process AirbyteMessages as usual with the addition of periodically
     * flushing buffer and writing data to destination storage
     *
     * @param msg [AirbyteMessage] to be processed
     * @throws Exception
     */
    @Throws(Exception::class)
    override fun acceptTracked(msg: AirbyteMessage) {
        Preconditions.checkState(hasStarted, "Cannot accept records until consumer has started")
        if (msg.type == AirbyteMessage.Type.RECORD) {
            val record = msg.record
            if (Strings.isNullOrEmpty(record.namespace)) {
                record.namespace = defaultNamespace
            }
            val stream = AirbyteStreamNameNamespacePair.fromRecordMessage(record)

            // if stream is not part of list of streams to sync to then throw invalid stream
            // exception
            if (!streamNames.contains(stream)) {
                throwUnrecognizedStream(catalog, msg)
            }

            if (!isValidRecord.apply(record.data)!!) {
                streamToIgnoredRecordCount[stream] =
                    streamToIgnoredRecordCount.getOrDefault(stream, 0L) + 1L
                return
            }

            val flushType = bufferingStrategy.addRecord(stream, msg)
            // if present means that a flush occurred
            if (flushType.isPresent) {
                if (BufferFlushType.FLUSH_ALL == flushType.get()) {
                    markStatesAsFlushedToDestination()
                } else if (BufferFlushType.FLUSH_SINGLE_STREAM == flushType.get()) {
                    if (stateManager.supportsPerStreamFlush()) {
                        // per-stream instance can handle flush of just a single stream
                        markStatesAsFlushedToDestination(stream)
                    }
                    /*
                     * We don't mark {@link AirbyteStateMessage} as committed in the case with GLOBAL/LEGACY because
                     * within a single stream being flushed it is not deterministic that all the AirbyteRecordMessages
                     * have been committed
                     */
                }
            }
        } else if (msg.type == AirbyteMessage.Type.STATE) {
            stateManager.addState(msg)
        } else {
            LOGGER.warn { "Unexpected message: ${msg.type}" }
        }
        periodicBufferFlush()
    }

    /**
     * After marking states as committed, return the state message to platform then clear state
     * messages to avoid resending the same state message to the platform. Also updates the next
     * time a buffer flush should occur since it is deterministic that when this method is called
     * all data has been successfully committed to destination
     */
    private fun markStatesAsFlushedToDestination() {
        stateManager.markPendingAsCommitted()
        stateManager.listCommitted()!!.forEach(outputRecordCollector)
        stateManager.clearCommitted()
        nextFlushDeadline = Instant.now().plus(bufferFlushFrequency)
    }

    private fun markStatesAsFlushedToDestination(stream: AirbyteStreamNameNamespacePair) {
        stateManager.markPendingAsCommitted(stream)
        stateManager.listCommitted()!!.forEach(outputRecordCollector)
        stateManager.clearCommitted()
        nextFlushDeadline = Instant.now().plus(bufferFlushFrequency)
    }

    /**
     * Periodically flushes buffered data to destination storage when exceeding flush deadline. Also
     * resets the last time a flush occurred
     */
    @Throws(Exception::class)
    private fun periodicBufferFlush() {
        // When the last time the buffered has been flushed exceed the frequency, flush the current
        // buffer before receiving incoming AirbyteMessage
        if (Instant.now().isAfter(nextFlushDeadline)) {
            LOGGER.info { "Periodic buffer flush started" }
            try {
                bufferingStrategy.flushAllBuffers()
                markStatesAsFlushedToDestination()
            } catch (e: Exception) {
                LOGGER.error(e) { "Periodic buffer flush failed" }
                throw e
            }
        }
    }

    /**
     * Cleans up buffer based on whether the sync was successful or some exception occurred. In the
     * case where a failure occurred we do a simple clean up any lingering data. Otherwise, flush
     * any remaining data that has been stored. This is fine even if the state has not been received
     * since this Airbyte promises at least once delivery
     *
     * @param hasFailed true if the stream replication failed partway through, false otherwise
     * @throws Exception
     */
    @Throws(Exception::class)
    override fun close(hasFailed: Boolean) {
        Preconditions.checkState(hasStarted, "Cannot close; has not started.")
        Preconditions.checkState(!hasClosed, "Has already closed.")
        hasClosed = true

        streamToIgnoredRecordCount.forEach { (pair: AirbyteStreamNameNamespacePair?, count: Long?)
            ->
            LOGGER.warn {
                "A total of $count record(s) of data from stream $pair were invalid and were ignored."
            }
        }
        if (hasFailed) {
            LOGGER.error { "executing on failed close procedure." }
        } else {
            LOGGER.info { "executing on success close procedure." }
            // When flushing the buffer, this will call the respective #flushBufferFunction which
            // bundles
            // the flush and commit operation, so if successful then mark state as committed
            bufferingStrategy.flushAllBuffers()
            markStatesAsFlushedToDestination()
        }
        bufferingStrategy.close()

        try {
            /*
             * TODO: (ryankfu) Remove usage of hasFailed with onClose after all destination connectors have been
             * updated to support checkpointing
             *
             * flushed is empty in 2 cases: 1. either it is full refresh (no state is emitted necessarily) 2. it
             * is stream but no states were flushed in both of these cases, if there was a failure, we should
             * not bother committing. otherwise attempt to commit
             */
            if (stateManager.listFlushed().isEmpty()) {
                // Not updating this class to track record count, because we want to kill it in
                // favor of the
                // AsyncStreamConsumer
                onClose.accept(hasFailed, HashMap())
            } else {
                /*
                 * if any state message was flushed that means we should try to commit what we have. if
                 * hasFailed=false, then it could be full success. if hasFailed=true, then going for partial
                 * success.
                 */
                // TODO what to do here?
                onClose.accept(false, HashMap())
            }

            stateManager.listCommitted()!!.forEach(outputRecordCollector)
        } catch (e: Exception) {
            LOGGER.error(e) { "Close failed." }
            throw e
        }
    }

    companion object {

        private fun throwUnrecognizedStream(
            catalog: ConfiguredAirbyteCatalog?,
            message: AirbyteMessage
        ) {
            throw IllegalArgumentException(
                String.format(
                    "Message contained record from a stream that was not in the catalog. \ncatalog: %s , \nmessage: %s",
                    Jsons.serialize(catalog),
                    Jsons.serialize(message)
                )
            )
        }
    }
}
