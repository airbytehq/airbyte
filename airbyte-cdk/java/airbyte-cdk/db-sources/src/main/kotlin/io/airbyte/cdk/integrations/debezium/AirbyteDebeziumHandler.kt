/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.integrations.debezium.internals.*
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.commons.util.AutoCloseableIterators
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.Instant
import java.time.temporal.ChronoUnit
import java.util.*
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.locks.ReentrantLock

private val LOGGER = KotlinLogging.logger {}
/**
 * This class acts as the bridge between Airbyte DB connectors and debezium. If a DB connector wants
 * to use debezium for CDC, it should use this class
 */
class AirbyteDebeziumHandler<T>(
    private val config: JsonNode,
    private val targetPosition: CdcTargetPosition<T>,
    private val trackSchemaHistory: Boolean,
    private val firstRecordWaitTime: Duration,
    private val queueSize: Int,
    private val addDbNameToOffsetState: Boolean
) {
    fun getIncrementalIterators(
        debeziumPropertiesManager: DebeziumPropertiesManager,
        eventConverter: DebeziumEventConverter,
        cdcSavedInfoFetcher: CdcSavedInfoFetcher,
        cdcStateHandler: CdcStateHandler
    ): AutoCloseableIterator<AirbyteMessage> {
        LOGGER.info { "Using CDC: true" }
        LOGGER.info {
            "Using DBZ version: ${DebeziumEngine::class.java.getPackage().implementationVersion}"
        }
        val offsetManager: AirbyteFileOffsetBackingStore =
            AirbyteFileOffsetBackingStore.Companion.initializeState(
                cdcSavedInfoFetcher.savedOffset,
                if (addDbNameToOffsetState)
                    Optional.ofNullable<String>(config[JdbcUtils.DATABASE_KEY].asText())
                else Optional.empty<String>(),
            )
        val schemaHistoryManager: Optional<AirbyteSchemaHistoryStorage> =
            if (trackSchemaHistory)
                Optional.of<AirbyteSchemaHistoryStorage>(
                    AirbyteSchemaHistoryStorage.Companion.initializeDBHistory(
                        cdcSavedInfoFetcher.savedSchemaHistory,
                        cdcStateHandler.compressSchemaHistoryForState(),
                    ),
                )
            else Optional.empty<AirbyteSchemaHistoryStorage>()
        val publisher = DebeziumRecordPublisher(debeziumPropertiesManager)
        val queue: CapacityReportingBlockingQueue<ChangeEvent<String?, String?>> =
            CapacityReportingBlockingQueue(
                queueSize,
                defaultQueueMaxMemoryUsageBytes(),
            ) { event ->
                // The ChangeEvent value is a JSON String; estimate its heap footprint as the
                // UTF-16 char array size (2 bytes per char).
                (event.value()?.length?.toLong() ?: 0L) * 2L
            }

        publisher.start(queue, offsetManager, schemaHistoryManager)
        // handle state machine around pub/sub logic.
        val eventIterator: AutoCloseableIterator<ChangeEventWithMetadata> =
            DebeziumRecordIterator(
                queue,
                targetPosition,
                { publisher.hasClosed() },
                DebeziumShutdownProcedure(queue, { publisher.close() }, { publisher.hasClosed() }),
                firstRecordWaitTime,
                config
            )

        val syncCheckpointDuration =
            if (config.has(DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION_PROPERTY))
                Duration.ofSeconds(
                    config[DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION_PROPERTY].asLong(),
                )
            else DebeziumIteratorConstants.SYNC_CHECKPOINT_DURATION
        val syncCheckpointRecords =
            if (config.has(DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY))
                config[DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS_PROPERTY].asLong()
            else DebeziumIteratorConstants.SYNC_CHECKPOINT_RECORDS.toLong()

        val messageProducer: DebeziumMessageProducer<T> =
            DebeziumMessageProducer<T>(
                cdcStateHandler,
                targetPosition,
                eventConverter,
                offsetManager,
                schemaHistoryManager,
            )

        // Usually sourceStateIterator requires airbyteStream as input. For DBZ iterator, stream is
        // not used
        // at all thus we will pass in null.
        val iterator: SourceStateIterator<ChangeEventWithMetadata> =
            SourceStateIterator(
                eventIterator,
                null,
                messageProducer,
                StateEmitFrequency(syncCheckpointRecords, syncCheckpointDuration),
            )
        return AutoCloseableIterators.fromIterator(iterator)
    }

    companion object {

        /**
         * We use 10000 as capacity cause the default queue size and batch size of debezium is :
         * [io.debezium.config.CommonConnectorConfig.DEFAULT_MAX_BATCH_SIZE]is 2048
         * [io.debezium.config.CommonConnectorConfig.DEFAULT_MAX_QUEUE_SIZE] is 8192
         */
        const val QUEUE_CAPACITY: Int = 10000

        /**
         * Fraction of the JVM max heap that the Airbyte-level CDC event queue is allowed to hold at
         * once. Combined with the count-based [QUEUE_CAPACITY], this prevents the queue from
         * exhausting the heap when individual change events are large (e.g. MongoDB documents
         * captured with pre-images, which can be hundreds of KB each).
         */
        const val QUEUE_MAX_MEMORY_USAGE_FRACTION: Double = 0.25

        /**
         * Default maximum approximate byte footprint of the CDC event queue, derived from the JVM
         * max heap. On a 6 GiB heap this is ~1.5 GB, well below the point where 10,000 large events
         * would OOM the container.
         */
        @JvmStatic
        fun defaultQueueMaxMemoryUsageBytes(): Long =
            (Runtime.getRuntime().maxMemory() * QUEUE_MAX_MEMORY_USAGE_FRACTION).toLong()

        @JvmStatic
        fun isAnyStreamIncrementalSyncMode(catalog: ConfiguredAirbyteCatalog): Boolean {
            return catalog.streams
                .map { obj: ConfiguredAirbyteStream -> obj.syncMode }
                .any { syncMode: SyncMode -> syncMode == SyncMode.INCREMENTAL }
        }
    }
}

/**
 * A [LinkedBlockingQueue] that, in addition to the standard count-based [capacity], tracks the
 * approximate heap footprint of the queued elements and blocks [put] once that footprint would
 * exceed [maxSizeInBytes].
 *
 * The Airbyte-level CDC event queue was previously bounded only by element count (default 10,000).
 * When individual change events are large (e.g. MongoDB documents captured with pre-images, which
 * can be hundreds of KB each) the queue could grow to several GB and exhaust the JVM heap, causing
 * OutOfMemoryErrors. This mirrors the byte-size bound Debezium already applies to its own internal
 * queue (`max.queue.size.in.bytes`).
 *
 * The count-based [capacity] remains as a secondary cap. A single element larger than
 * [maxSizeInBytes] is still admitted when the queue is empty, so an oversized event can never
 * deadlock the pipeline.
 *
 * @param bytesEstimator returns the approximate heap size, in bytes, of a queued element.
 */
class CapacityReportingBlockingQueue<E>(
    capacity: Int,
    private val maxSizeInBytes: Long,
    private val bytesEstimator: (E) -> Long,
) : LinkedBlockingQueue<E>(capacity) {
    private var lastReport: Instant = Instant.MIN
    private var puts = AtomicLong()
    private var polls = AtomicLong()
    private val currentByteSize = AtomicLong()
    private val byteSizeLock = ReentrantLock()
    private val belowByteThreshold = byteSizeLock.newCondition()

    /** Current approximate heap footprint, in bytes, of the elements held in the queue. */
    val currentByteSizeEstimate: Long
        get() = currentByteSize.get()

    private fun estimateByteSize(e: E): Long =
        try {
            maxOf(0L, bytesEstimator(e))
        } catch (ex: Exception) {
            0L
        }

    private fun reportQueueUtilization(put: Long = 0L, poll: Long = 0L) {
        if (Duration.between(lastReport, Instant.now()) > REPORT_DURATION) {
            LOGGER.info {
                "CDC events queue stats: " +
                    "size=${this.size}, " +
                    "cap=${this.remainingCapacity()}, " +
                    "bytes=${currentByteSize.get()}, " +
                    "maxBytes=$maxSizeInBytes, " +
                    "puts=${puts.addAndGet(put)}, " +
                    "polls=${polls.addAndGet(poll)}"
            }
            synchronized(this) { lastReport = Instant.now() }
        }
    }

    @Throws(InterruptedException::class)
    override fun put(e: E) {
        val elementBytes = estimateByteSize(e)
        byteSizeLock.lockInterruptibly()
        try {
            // Block until adding this element keeps us under the byte budget. Always admit an
            // element into an empty queue so an oversized event can never deadlock the pipeline.
            while (!isEmpty() && currentByteSize.get() + elementBytes > maxSizeInBytes) {
                belowByteThreshold.await()
            }
        } finally {
            byteSizeLock.unlock()
        }
        reportQueueUtilization(put = 1L)
        // Account for the bytes before the (count-capacity) blocking put so consumers never
        // under-count the in-flight memory footprint.
        currentByteSize.addAndGet(elementBytes)
        try {
            super.put(e)
        } catch (ex: InterruptedException) {
            currentByteSize.addAndGet(-elementBytes)
            signalBelowByteThreshold()
            throw ex
        }
    }

    override fun poll(): E? {
        reportQueueUtilization(poll = 1L)
        val e = super.poll()
        onRemoved(e)
        return e
    }

    @Throws(InterruptedException::class)
    override fun poll(timeout: Long, unit: TimeUnit): E? {
        reportQueueUtilization(poll = 1L)
        val e = super.poll(timeout, unit)
        onRemoved(e)
        return e
    }

    @Throws(InterruptedException::class)
    override fun take(): E {
        reportQueueUtilization(poll = 1L)
        val e = super.take()
        onRemoved(e)
        return e
    }

    private fun onRemoved(e: E?) {
        if (e == null) {
            return
        }
        currentByteSize.addAndGet(-estimateByteSize(e))
        signalBelowByteThreshold()
    }

    private fun signalBelowByteThreshold() {
        byteSizeLock.lock()
        try {
            belowByteThreshold.signalAll()
        } finally {
            byteSizeLock.unlock()
        }
    }

    companion object {
        private val REPORT_DURATION: Duration = Duration.of(10, ChronoUnit.SECONDS)
    }
}
