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
    /**
     * A [LinkedBlockingQueue] that periodically logs how full it is.
     *
     * The queue is bounded by element **count** only. That is deliberate: connectors that carry
     * large change events (e.g. MongoDB documents captured with pre-images) size the count so that
     * `count * max_event_size` fits comfortably in the heap, rather than relying on a byte
     * estimate. The byte figures below are therefore **telemetry, not a bound** -- they exist so
     * that a heap problem is diagnosable from one log line instead of requiring a fresh
     * investigation. The accounting is intentionally lock-free and never blocks a producer or
     * consumer; being slightly stale or slightly off does not matter for a log line.
     *
     * Note that the byte estimate counts only the JSON value string. Each queued element is a
     * `io.debezium.embedded.EmbeddedEngineChangeEvent`, which also retains the key and the original
     * Kafka Connect `SourceRecord`, so true retained heap is meaningfully higher than what is
     * reported here.
     */
    internal inner class CapacityReportingBlockingQueue<E>(capacity: Int) :
        LinkedBlockingQueue<E>(capacity) {
        private var lastReport: Instant = Instant.MIN
        private var puts = AtomicLong()
        private var polls = AtomicLong()
        private val estimatedBytes = AtomicLong()

        /**
         * Approximate heap footprint of a queued element, in bytes, from the length of its JSON
         * value (UTF-16, 2 bytes per char). Returns 0 for anything unrecognised so that this can
         * never throw on the hot path.
         */
        private fun estimateBytes(e: E?): Long =
            when (e) {
                is ChangeEvent<*, *> -> ((e.value() as? String)?.length?.toLong() ?: 0L) * 2L
                else -> 0L
            }

        private fun reportQueueUtilization() {
            if (Duration.between(lastReport, Instant.now()) > REPORT_DURATION) {
                val size = this.size
                val bytes = estimatedBytes.get()
                val runtime = Runtime.getRuntime()
                LOGGER.info {
                    "CDC events queue stats: " +
                        "size=$size, " +
                        "cap=${this.remainingCapacity()}, " +
                        "estimatedBytes=$bytes, " +
                        "avgBytesPerEvent=${if (size > 0) bytes / size else 0}, " +
                        "heapUsed=${runtime.totalMemory() - runtime.freeMemory()}, " +
                        "heapMax=${runtime.maxMemory()}, " +
                        "puts=${puts.get()}, " +
                        "polls=${polls.get()}"
                }
                synchronized(this) { lastReport = Instant.now() }
            }
        }

        @Throws(InterruptedException::class)
        override fun put(e: E) {
            puts.incrementAndGet()
            estimatedBytes.addAndGet(estimateBytes(e))
            reportQueueUtilization()
            try {
                super.put(e)
            } catch (ex: InterruptedException) {
                estimatedBytes.addAndGet(-estimateBytes(e))
                throw ex
            }
        }

        override fun poll(): E? = onRemoved(super.poll())

        @Throws(InterruptedException::class)
        override fun poll(timeout: Long, unit: TimeUnit): E? = onRemoved(super.poll(timeout, unit))

        @Throws(InterruptedException::class) override fun take(): E = onRemoved(super.take())!!

        private fun onRemoved(e: E?): E? {
            if (e != null) {
                polls.incrementAndGet()
                estimatedBytes.addAndGet(-estimateBytes(e))
            }
            reportQueueUtilization()
            return e
        }
    }

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
            CapacityReportingBlockingQueue(queueSize)

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

        private val REPORT_DURATION: Duration = Duration.of(10, ChronoUnit.SECONDS)

        /**
         * We use 10000 as capacity cause the default queue size and batch size of debezium is :
         * [io.debezium.config.CommonConnectorConfig.DEFAULT_MAX_BATCH_SIZE]is 2048
         * [io.debezium.config.CommonConnectorConfig.DEFAULT_MAX_QUEUE_SIZE] is 8192
         */
        const val QUEUE_CAPACITY: Int = 10000

        @JvmStatic
        fun isAnyStreamIncrementalSyncMode(catalog: ConfiguredAirbyteCatalog): Boolean {
            return catalog.streams
                .map { obj: ConfiguredAirbyteStream -> obj.syncMode }
                .any { syncMode: SyncMode -> syncMode == SyncMode.INCREMENTAL }
        }
    }
}
