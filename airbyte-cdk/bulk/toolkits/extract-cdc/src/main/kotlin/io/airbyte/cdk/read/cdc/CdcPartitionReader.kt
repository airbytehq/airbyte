/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.read.cdc

import edu.umd.cs.findbugs.annotations.SuppressFBWarnings
import io.airbyte.cdk.StreamIdentifier
import io.airbyte.cdk.command.OpaqueStateValue
import io.airbyte.cdk.output.DataChannelMedium.SOCKET
import io.airbyte.cdk.output.DataChannelMedium.STDIO
import io.airbyte.cdk.output.OutputMessageRouter
import io.airbyte.cdk.read.GlobalFeedBootstrap
import io.airbyte.cdk.read.PartitionReadCheckpoint
import io.airbyte.cdk.read.PartitionReader
import io.airbyte.cdk.read.Resource
import io.airbyte.cdk.read.ResourceAcquirer
import io.airbyte.cdk.read.ResourceType
import io.airbyte.cdk.read.ResourceType.RESOURCE_DB_CONNECTION
import io.airbyte.cdk.read.ResourceType.RESOURCE_OUTPUT_SOCKET
import io.airbyte.cdk.read.Stream
import io.airbyte.cdk.read.UnlimitedTimePartitionReader
import io.airbyte.cdk.read.cdc.DebeziumPropertiesBuilder.Companion.AIRBYTE_HEARTBEAT_TIMEOUT_SECONDS
import io.airbyte.cdk.read.generatePartitionId
import io.airbyte.protocol.models.v0.StreamDescriptor
import io.debezium.engine.ChangeEvent
import io.debezium.engine.DebeziumEngine
import io.debezium.engine.format.Json
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Duration
import java.time.LocalDateTime
import java.util.*
import java.util.concurrent.atomic.AtomicBoolean
import java.util.concurrent.atomic.AtomicLong
import java.util.concurrent.atomic.AtomicReference
import java.util.function.Consumer
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import org.apache.kafka.connect.source.SourceRecord

/** [PartitionReader] implementation for CDC with Debezium. */
@SuppressFBWarnings(value = ["NP_NONNULL_RETURN_VIOLATION"], justification = "Micronaut DI")
class CdcPartitionReader<T : Comparable<T>>(
    val resourceAcquirer: ResourceAcquirer,
    val readerOps: CdcPartitionReaderDebeziumOperations<T>,
    val upperBound: T,
    val debeziumProperties: Map<String, String>,
    val startingOffset: DebeziumOffset,
    val startingSchemaHistory: DebeziumSchemaHistory?,
    val isInputStateSynthetic: Boolean,
    val feedBootstrap: GlobalFeedBootstrap
) : UnlimitedTimePartitionReader {
    private val log = KotlinLogging.logger {}
    private val acquiredResources = AtomicReference<Map<ResourceType, AcquiredResource>>()
    private val engineShuttingDown: AtomicBoolean = AtomicBoolean(false)
    private lateinit var stateFilesAccessor: DebeziumStateFilesAccessor
    private lateinit var decoratedProperties: Properties
    private lateinit var engine: DebeziumEngine<ChangeEvent<String?, String?>>
    lateinit var outputMessageRouter: OutputMessageRouter

    internal val closeReasonReference = AtomicReference<CloseReason>()
    internal val numEvents = AtomicLong()
    internal val numTombstones = AtomicLong()
    internal val numHeartbeats = AtomicLong()
    internal val numDiscardedRecords = AtomicLong()
    internal val numEmittedRecords = AtomicLong()
    internal val numEventsWithoutSourceRecord = AtomicLong()
    internal val numSourceRecordsWithoutPosition = AtomicLong()
    internal val numEventValuesWithoutPosition = AtomicLong()

    // Track last event time for watchdog timeout monitoring
    private val lastEventTime = AtomicReference(LocalDateTime.now())
    private var watchdogJob: Job? = null
    @Volatile private var watchdogShouldStop = false

    private var partitionId: String = generatePartitionId(4)

    interface AcquiredResource : AutoCloseable {
        val resource: Resource.Acquired?
    }

    override fun tryAcquireResources(): PartitionReader.TryAcquireResourcesStatus {
        fun innerAcquireResources(
            resourcesType: List<ResourceType>
        ): Map<ResourceType, AcquiredResource>? {
            val resources: Map<ResourceType, Resource.Acquired>? =
                resourceAcquirer.tryAcquire(resourcesType)
            return resources
                ?.map {
                    it.key to
                        object : AcquiredResource {
                            override val resource: Resource.Acquired = it.value
                            override fun close() {
                                resource.close()
                            }
                        }
                }
                ?.toMap()
        }

        val resourceType: List<ResourceType> =
            when (feedBootstrap.dataChannelMedium) {
                SOCKET -> listOf(RESOURCE_DB_CONNECTION, RESOURCE_OUTPUT_SOCKET)
                STDIO -> listOf(RESOURCE_DB_CONNECTION)
            }
        val resources: Map<ResourceType, AcquiredResource> =
            innerAcquireResources(resourceType)
                ?: return PartitionReader.TryAcquireResourcesStatus.RETRY_LATER

        acquiredResources.set(resources)
        this.stateFilesAccessor = DebeziumStateFilesAccessor()

        outputMessageRouter =
            OutputMessageRouter(
                feedBootstrap.dataChannelMedium,
                feedBootstrap.dataChannelFormat,
                feedBootstrap.outputConsumer,
                mapOf("partition_id" to partitionId),
                feedBootstrap,
                acquiredResources
                    .get()
                    .filter { it.value.resource != null }
                    .map { it.key to it.value.resource!! }
                    .toMap()
            )
        return PartitionReader.TryAcquireResourcesStatus.READY_TO_RUN
    }

    override fun releaseResources() {
        if (::outputMessageRouter.isInitialized) {
            outputMessageRouter.close()
        }

        stateFilesAccessor.close()
        acquiredResources.getAndSet(null)?.forEach { it.value.close() }
    }

    override suspend fun run() {
        stateFilesAccessor.writeOffset(startingOffset)
        if (startingSchemaHistory != null) {
            stateFilesAccessor.writeSchema(startingSchemaHistory)
        }
        decoratedProperties =
            DebeziumPropertiesBuilder()
                .with(debeziumProperties)
                .withOffsetFile(stateFilesAccessor.offsetFilePath)
                .withSchemaHistoryFile(stateFilesAccessor.schemaFilePath)
                .build()
        engine =
            DebeziumEngine.create(Json::class.java)
                .using(decoratedProperties)
                .using(ConnectorCallback())
                .using(CompletionCallback())
                .notifying(EventConsumer())
                .build()
        val debeziumVersion: String = DebeziumEngine::class.java.getPackage().implementationVersion
        log.info { "Running Debezium engine version $debeziumVersion." }
        val engineException = AtomicReference<Throwable>()
        val thread = Thread(engine, "debezium-engine")
        thread.setUncaughtExceptionHandler { _, e: Throwable -> engineException.set(e) }
        thread.start()

        // Start watchdog coroutine if timeout is configured
        val timeoutDuration =
            debeziumProperties[AIRBYTE_HEARTBEAT_TIMEOUT_SECONDS]?.let {
                Duration.ofSeconds(it.toLongOrNull() ?: 0L).takeIf { duration ->
                    duration.seconds > 0
                }
            }
        if (timeoutDuration != null) {
            watchdogShouldStop = false
            lastEventTime.set(LocalDateTime.now())
            watchdogJob = CoroutineScope(Dispatchers.IO).launch { startWatchdog(timeoutDuration) }
        }

        try {
            withContext(Dispatchers.IO) { thread.join() }
        } catch (e: Throwable) {
            // This catches any exceptions thrown by join()
            // but also by the kotlin coroutine dispatcher, like TimeoutCancellationException.
            engineException.compareAndSet(null, e)
        } finally {
            watchdogShouldStop = true
            watchdogJob?.cancel()
        }
        // Print a nice log message and re-throw any exception.
        val exception: Throwable? = engineException.get()
        val summary: Map<String, Any?> =
            mapOf(
                    "debezium-version" to debeziumVersion,
                    "records-emitted" to numEmittedRecords.get(),
                    "records-discarded" to numDiscardedRecords.get(),
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
        val offset: DebeziumOffset = stateFilesAccessor.readUpdatedOffset(startingOffset)
        val schemaHistory: DebeziumSchemaHistory? =
            if (DebeziumPropertiesBuilder().with(decoratedProperties).expectsSchemaHistoryFile) {
                stateFilesAccessor.readSchema()
            } else {
                null
            }
        val serializedState: OpaqueStateValue = readerOps.serializeState(offset, schemaHistory)
        return PartitionReadCheckpoint(
            serializedState,
            numEmittedRecords.get(),
            when (feedBootstrap.dataChannelMedium) {
                SOCKET -> partitionId
                STDIO -> null
            }
        )
    }

    /**
     * Watchdog coroutine that monitors for timeout when no events are received from Debezium. This
     * is necessary because Debezium may not emit any events (including heartbeats) when the
     * database has no changes, causing the sync to hang indefinitely.
     *
     * The watchdog waits for exactly the timeout duration, then checks once. If any event is
     * received during that time, the watchdog is cancelled by the event consumer.
     */
    private suspend fun startWatchdog(timeoutDuration: Duration) {
        log.info { "Starting watchdog with timeout of ${timeoutDuration.seconds} seconds" }
        delay(timeoutDuration.toMillis())

        // If we reach here, no event was received within the timeout period
        // Check if we should still proceed (engine might have closed for other reasons)
        if (watchdogShouldStop || closeReasonReference.get() != null) {
            log.info { "Watchdog woke up but engine already stopped" }
            return
        }

        log.info {
            "Watchdog timeout: no events received for ${timeoutDuration.toMinutes()} minutes. " +
                "Records emitted: ${numEmittedRecords.get()}. Shutting down Debezium engine."
        }

        if (closeReasonReference.compareAndSet(null, CloseReason.WATCHDOG_TIMEOUT)) {
            engineShuttingDown.set(true)
            runBlocking { launch(Dispatchers.IO + Job()) { engine.close() } }
        }
    }

    inner class EventConsumer() : Consumer<ChangeEvent<String?, String?>> {

        private var lastHeartbeatPosition: T? = null
        private var lastHeartbeatTime: LocalDateTime? = null
        // Only enable heartbeat timeout if explicitly configured
        private val heartbeatTimeoutDuration: Duration? =
            debeziumProperties[AIRBYTE_HEARTBEAT_TIMEOUT_SECONDS]?.let {
                Duration.ofSeconds(it.toLongOrNull() ?: 0L).takeIf { duration ->
                    duration.seconds > 0
                }
            }

        override fun accept(changeEvent: ChangeEvent<String?, String?>) {
            // Stop watchdog once we receive any event - connection is working
            if (watchdogJob != null && !watchdogShouldStop) {
                log.info { "Received first event from Debezium, stopping watchdog" }
                watchdogShouldStop = true
                watchdogJob?.cancel()
            }

            val event = DebeziumEvent(changeEvent)
            val eventType: EventType = emitRecord(event)
            if (!engineShuttingDown.get()) {
                updateCounters(event, eventType)
            }
            // Look for reasons to close down the engine.
            val closeReason: CloseReason = findCloseReason(event, eventType) ?: return
            // At this point, if we haven't returned already, we want to close down the engine.
            if (!closeReasonReference.compareAndSet(null, closeReason)) {
                // An earlier event has already triggered closing down the engine, do nothing.
                return
            }
            // At this point, if we haven't returned already, we need to close down the engine.
            log.info { "Shutting down Debezium engine: ${closeReason.message}." }
            // TODO : send close analytics message
            engineShuttingDown.set(true)
            runBlocking() { launch(Dispatchers.IO + Job()) { engine.close() } }
        }

        private fun emitRecord(event: DebeziumEvent): EventType {
            if (event.isTombstone) {
                // Debezium outputs a tombstone event that has a value of null. This is an artifact
                // of how it interacts with kafka. We want to ignore it. More on the tombstone:
                // https://debezium.io/documentation/reference/stable/transformations/event-flattening.html
                return EventType.TOMBSTONE
            }
            if (event.isHeartbeat) {
                // Heartbeats are only used for their position.
                return EventType.HEARTBEAT
            }
            if (event.key == null) {
                // Sometimes, presumably due to bugs in Debezium, the key isn't valid JSON.
                return EventType.KEY_JSON_INVALID
            }
            if (event.value == null) {
                // Sometimes, presumably due to bugs in Debezium, the value isn't valid JSON.
                return EventType.VALUE_JSON_INVALID
            }
            val streamId = findStreamIdByRecord(event.key, event.value)
            val stream: Stream =
                feedBootstrap.feeds.filter { it is Stream }.find { (it as Stream).id == streamId }
                    as? Stream
                    ?: return EventType.RECORD_DISCARDED_BY_STREAM_ID
            val deserializedRecord: DeserializedRecord =
                readerOps.deserializeRecord(event.key, event.value, stream)
                    ?: return EventType.RECORD_DISCARDED_BY_DESERIALIZE
            val recordAcceptor =
                outputMessageRouter.recordAcceptors[streamId]
                    ?: run {
                        log.warn {
                            "No record acceptor found for stream $streamId, skipping record emission."
                        }
                        return EventType.RECORD_DISCARDED_BY_STREAM_ID
                    }

            // Emit the record at the end of the happy path.
            when (engineShuttingDown.get()) {
                // While the engine is shutting down, we emit records in our thread to prevent
                // debezium from unexpectedly killing the thread.
                // As this may lead to corrupt hald records or to causing an unexpected socket
                // closure.
                true ->
                    runBlocking(Dispatchers.IO) {
                        recordAcceptor.invoke(deserializedRecord.data, deserializedRecord.changes)
                        updateCounters(event, EventType.RECORD_EMITTED)
                    }
                // While the engine is running normally, we can emit records synchronously for
                // better performance.
                false -> recordAcceptor.invoke(deserializedRecord.data, deserializedRecord.changes)
            }
            return EventType.RECORD_EMITTED
        }

        private fun findStreamIdByRecord(
            key: DebeziumRecordKey,
            value: DebeziumRecordValue
        ): StreamIdentifier? {
            val name: String = readerOps.findStreamName(key, value) ?: return null
            val namespace: String? = readerOps.findStreamNamespace(key, value)
            val desc: StreamDescriptor = StreamDescriptor().withNamespace(namespace).withName(name)
            return StreamIdentifier.from(desc)
        }

        private fun updateCounters(event: DebeziumEvent, eventType: EventType) {
            numEvents.incrementAndGet()
            if (event.sourceRecord == null) {
                numEventsWithoutSourceRecord.incrementAndGet()
            }
            when (eventType) {
                EventType.TOMBSTONE -> numTombstones
                EventType.HEARTBEAT -> numHeartbeats
                EventType.KEY_JSON_INVALID,
                EventType.VALUE_JSON_INVALID,
                EventType.RECORD_DISCARDED_BY_DESERIALIZE,
                EventType.RECORD_DISCARDED_BY_STREAM_ID -> numDiscardedRecords
                EventType.RECORD_EMITTED -> numEmittedRecords
            }.incrementAndGet()
        }

        private fun findCloseReason(event: DebeziumEvent, eventType: EventType): CloseReason? {
            if (isInputStateSynthetic && eventType != EventType.HEARTBEAT) {
                // Special case where the engine started with a synthetic offset:
                // don't even consider closing the engine unless handling a heartbeat event.
                // For some databases, such as Oracle, Debezium actually needs to snapshot the
                // schema in order to collect the database schema history and there's no point
                // in interrupting it until the snapshot is done.
                return null
            }

            val currentPosition: T? = position(event.sourceRecord) ?: position(event.value)

            // Only check for heartbeat timeout if it's configured AND this is a heartbeat event
            if (eventType == EventType.HEARTBEAT && heartbeatTimeoutDuration != null) {
                val now = LocalDateTime.now()

                // Check if heartbeat position is progressing (LSN should increase)
                //  - If lastHeartbeatPosition is null (first heartbeat) → isProgressing = true
                //  - If currentPosition is null → skip timeout check (return early)
                //  - Otherwise → isProgressing = (currentPosition > lastHeartbeatPosition)
                if (currentPosition == null) {
                    return null
                }
                val isProgressing = lastHeartbeatPosition?.let { currentPosition > it } ?: true
                if (isProgressing) {
                    lastHeartbeatPosition = currentPosition
                    lastHeartbeatTime = now
                    log.info { "Heartbeat progressing to position: $currentPosition" }
                } else {
                    val timeSinceLastProgress = Duration.between(lastHeartbeatTime!!, now)
                    if (timeSinceLastProgress > heartbeatTimeoutDuration) {
                        log.info {
                            "Heartbeat timeout: no progress for ${timeSinceLastProgress.toMinutes()} minutes. " +
                                "Last position: $lastHeartbeatPosition, current: $currentPosition"
                        }
                        return CloseReason.HEARTBEAT_NOT_PROGRESSING
                    }
                    log.info {
                        "Heartbeat not progressing, time since last progress: ${timeSinceLastProgress.toSeconds()}s"
                    }
                }
            }

            if (currentPosition == null || currentPosition < upperBound) {
                return null
            }
            // Close because the current event is past the sync upper bound.
            return when (eventType) {
                EventType.TOMBSTONE,
                EventType.HEARTBEAT -> CloseReason.HEARTBEAT_OR_TOMBSTONE_REACHED_TARGET_POSITION
                EventType.KEY_JSON_INVALID,
                EventType.VALUE_JSON_INVALID,
                EventType.RECORD_EMITTED,
                EventType.RECORD_DISCARDED_BY_DESERIALIZE,
                EventType.RECORD_DISCARDED_BY_STREAM_ID ->
                    CloseReason.RECORD_REACHED_TARGET_POSITION
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

    private enum class EventType {
        TOMBSTONE,
        HEARTBEAT,
        KEY_JSON_INVALID,
        VALUE_JSON_INVALID,
        RECORD_DISCARDED_BY_DESERIALIZE,
        RECORD_DISCARDED_BY_STREAM_ID,
        RECORD_EMITTED,
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
        HEARTBEAT_OR_TOMBSTONE_REACHED_TARGET_POSITION(
            "heartbeat or tombstone indicates that WAL consumption has reached the target position"
        ),
        RECORD_REACHED_TARGET_POSITION(
            "record indicates that WAL consumption has reached the target position"
        ),
        HEARTBEAT_NOT_PROGRESSING(
            "heartbeat position has not progressed for an extended period, indicating database is idle"
        ),
        WATCHDOG_TIMEOUT(
            "no events received from Debezium within the configured timeout period, indicating database is idle or connection is stuck"
        ),
    }
}
