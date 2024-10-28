/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import io.airbyte.cdk.output.OutputConsumer
import io.airbyte.cdk.read.ConcurrencyResource
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.util.Jsons
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.debezium.embedded.EmbeddedEngineChangeEvent
import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.debezium.engine.format.Json
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.Properties
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import java.util.function.Consumer
import kotlin.coroutines.CoroutineContext
import kotlin.coroutines.coroutineContext
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.isActive
import kotlinx.coroutines.withContext
import org.apache.kafka.connect.source.SourceRecord

/** [PartitionReader] implementation for CDC with Debezium. */
class CdcPartitionReader<T : Comparable<T>>(
    val concurrencyResource: ConcurrencyResource,
    val outputConsumer: OutputConsumer,
    val readerOps: CdcPartitionReaderDebeziumOperations<T>,
    val upperBound: T,
    val input: DebeziumInput,
) : PartitionReader {
    private val log = KotlinLogging.logger {}
    private val acquiredThread = AtomicReference<ConcurrencyResource.AcquiredThread>()
    private lateinit var stateFilesAccessor: DebeziumStateFilesAccessor
    private lateinit var properties: Properties
    private lateinit var engine: DebeziumEngine<ChangeEvent<String?, String?>>

    internal val closeReasonReference = AtomicReference<CloseReason>()
    internal val numEvents = AtomicLong()
    internal val numTombstones = AtomicLong()
    internal val numHeartbeats = AtomicLong()
    internal val numRecords = AtomicLong()
    internal val numEventsWithoutSourceRecord = AtomicLong()
    internal val numSourceRecordsWithoutPosition = AtomicLong()
    internal val numEventValuesWithoutPosition = AtomicLong()

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        val acquiredThread: ConcurrencyResource.AcquiredThread =
            concurrencyResource.tryAcquire()
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER
        this.acquiredThread.set(acquiredThread)
        this.stateFilesAccessor = DebeziumStateFilesAccessor()
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override fun releaseResources() {
        stateFilesAccessor.close()
        acquiredThread.getAndSet(null)?.close()
    }

    override suspend fun run() {
        stateFilesAccessor.writeOffset(input.state.offset)
        if (input.state.schemaHistory != null) {
            stateFilesAccessor.writeSchema(input.state.schemaHistory)
        }
        properties =
            DebeziumPropertiesBuilder()
                .with(input.properties)
                .withOffsetFile(stateFilesAccessor.offsetFilePath)
                .withSchemaHistoryFile(stateFilesAccessor.schemaFilePath)
                .build()
        engine =
            DebeziumEngine.create(Json::class.java)
                .using(properties)
                .using(ConnectorCallback())
                .using(CompletionCallback())
                .notifying(EventConsumer(coroutineContext))
                .build()
        val debeziumVersion: String = DebeziumEngine::class.java.getPackage().implementationVersion
        log.info { "Running Debezium engine version $debeziumVersion." }
        val engineException = AtomicReference<Throwable>()
        val thread = Thread(engine, "debezium-engine")
        thread.setUncaughtExceptionHandler { _, e: Throwable -> engineException.set(e) }
        thread.start()
        withContext(Dispatchers.IO) { thread.join() }
        val exception: Throwable? = engineException.get()
        val summary: Map<String, Any?> =
            mapOf(
                    "debezium-version" to debeziumVersion,
                    "records" to numRecords.get(),
                    "heartbeats" to numHeartbeats.get(),
                    "tombstones" to numTombstones.get(),
                    "events" to numEvents.get(),
                    "events-without-source-record" to numEventsWithoutSourceRecord.get(),
                    "source-records-without-position" to numSourceRecordsWithoutPosition.get(),
                    "event-values-without-position" to numEventValuesWithoutPosition.get(),
                    "close-reason" to closeReasonReference.get(),
                    "exception" to exception?.let { it::class },
                )
                .filterValues { it != null }
        log.info { "Debezium Engine has shut down and relinquished control, summary: $summary." }
        if (exception != null) throw exception
    }

    override fun checkpoint(): PartitionReadCheckpoint {
        val offset: DebeziumOffset = stateFilesAccessor.readUpdatedOffset(input.state.offset)
        val schemaHistory: DebeziumSchemaHistory? =
            if (DebeziumPropertiesBuilder().with(properties).expectsSchemaHistoryFile) {
                stateFilesAccessor.readSchema()
            } else {
                null
            }
        val output = DebeziumState(offset, schemaHistory)
        return PartitionReadCheckpoint(readerOps.serialize(output), numRecords.get())
    }

    inner class EventConsumer(
        private val coroutineContext: CoroutineContext,
    ) : Consumer<ChangeEvent<String?, String?>> {

        override fun accept(event: ChangeEvent<String?, String?>) {
            numEvents.incrementAndGet()
            // Get SourceRecord object if possible.
            // This object is the preferred way to obtain the current position.
            val sourceRecord: SourceRecord? =
                (event as? EmbeddedEngineChangeEvent<*, *, *>)?.sourceRecord()
            if (sourceRecord == null) numEventsWithoutSourceRecord.incrementAndGet()
            // Debezium outputs a tombstone event that has a value of null. This is an artifact
            // of how it interacts with kafka. We want to ignore it. More on the tombstone:
            // https://debezium.io/documentation/reference/stable/transformations/event-flattening.html
            val debeziumRecordValue: DebeziumRecordValue? =
                event.value()?.let { DebeziumRecordValue(Jsons.readTree(it)) }
            // Process records, ignoring heartbeats which are only used for completion checks.
            val isRecord: Boolean
            if (debeziumRecordValue == null) {
                isRecord = false
                numTombstones.incrementAndGet()
            } else if (debeziumRecordValue.isHeartbeat) {
                isRecord = false
                numHeartbeats.incrementAndGet()
            } else {
                isRecord = true
                val debeziumRecordKey = DebeziumRecordKey(Jsons.readTree(event.key()))
                val airbyteRecord: AirbyteRecordMessage =
                    readerOps.toAirbyteRecordMessage(debeziumRecordKey, debeziumRecordValue)
                outputConsumer.accept(airbyteRecord)
                numRecords.incrementAndGet()
            }
            // Look for reasons to close down the engine.
            val closeReason: CloseReason? = run {
                if (!coroutineContext.isActive) {
                    return@run CloseReason.TIMEOUT
                }
                val currentPosition: T? = position(sourceRecord) ?: position(debeziumRecordValue)
                if (currentPosition == null || currentPosition < upperBound) {
                    return@run null
                }
                // Close because the current event is past the sync upper bound.
                if (isRecord) {
                    CloseReason.RECORD_REACHED_TARGET_POSITION
                } else {
                    CloseReason.HEARTBEAT_OR_TOMBSTONE_REACHED_TARGET_POSITION
                }
            }
            // Idempotent engine shutdown.
            if (closeReason != null && closeReasonReference.compareAndSet(null, closeReason)) {
                log.info { "Shutting down Debezium engine: ${closeReason.message}." }
                // TODO : send close analytics message
                Thread({ engine.close() }, "debezium-close").start()
            }
        }

        private fun position(sourceRecord: SourceRecord?): T? {
            if (sourceRecord == null) return null
            val sourceRecordPosition: T? = readerOps.position(sourceRecord)
            if (sourceRecordPosition == null) {
                numSourceRecordsWithoutPosition.incrementAndGet()
                return null
            }
            return sourceRecordPosition
        }

        private fun position(debeziumRecordValue: DebeziumRecordValue?): T? {
            if (debeziumRecordValue == null) return null
            val debeziumRecordValuePosition: T? = readerOps.position(debeziumRecordValue)
            if (debeziumRecordValuePosition == null) {
                numEventValuesWithoutPosition.incrementAndGet()
                return null
            }
            return debeziumRecordValuePosition
        }
    }

    inner class CompletionCallback : DebeziumEngine.CompletionCallback {
        override fun handle(success: Boolean, message: String?, error: Throwable?) {
            if (success) {
                log.info { "Debezium engine has shut down successfully: $message" }
            } else {
                // There are cases where Debezium doesn't succeed but only fills the message field.
                val e: Throwable = error ?: RuntimeException(message)
                log.warn(e) { "Debezium engine has NOT shut down successfully: $message" }
                throw e
            }
        }
    }

    inner class ConnectorCallback : DebeziumEngine.ConnectorCallback {
        override fun connectorStarted() {
            log.info { "Debezium connector started" }
        }

        override fun connectorStopped() {
            log.info { "Debezium connector stopped" }
        }

        override fun taskStarted() {
            log.info { "Debezium task started" }
        }

        override fun taskStopped() {
            log.info { "Debezium Task stopped" }
        }
    }

    enum class CloseReason(val message: String) {
        TIMEOUT("timed out"),
        HEARTBEAT_OR_TOMBSTONE_REACHED_TARGET_POSITION(
            "heartbeat or tombstone indicates that WAL consumption has reached the target position"
        ),
        RECORD_REACHED_TARGET_POSITION(
            "record indicates that WAL consumption has reached the target position"
        ),
    }
}
